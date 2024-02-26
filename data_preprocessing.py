import pandas as pd
import json
from datetime import datetime
from scipy.stats import pearsonr


# Load the Excel file
excel_path = 'ASFI List_reduced.xlsx'
df = pd.read_excel(excel_path)
df = pd.read_excel(excel_path, converters={
    'downturn_start': str,  # Convert downturn_start to string
    'downturn_end': str,    # Convert downturn_end to string
    'start_date': str,       # Convert start_date to string
    'end_date': str          # Convert end_date to string
})

# Load the JSON file
json_path = 'selected_projects.json'
with open(json_path, 'r') as file:
    data = json.load(file)

# Add new columns to the DataFrame for the metrics
metrics = ['num_issues','issue_average_close_time', 'pr_ave_merge_time', 'ratio_mergedPR','num_merged_pr', 'num_open_pr', 'num_closed_pr', 'ave_pr_comments']
periods = ['pre_downturn', 'downturn', 'post_downturn']

for metric in metrics:
    for period in periods:
        df[f'{metric}_{period}'] = None


# Helper functions
def get_date_range_from_json(json_data):
    all_dates = []
    for stats in ['monthly_issue_stats', 'monthly_pr_stats',  'monthly_pr_comments']:
        if stats in json_data:
            all_dates.extend(json_data[stats].keys())
    if all_dates:
        all_dates.sort()
        return all_dates[0], all_dates[-1]
    return None, None

def calculate_average_for_period(data, start, end, metric):
    relevant_data = []
    for k, v in data.items():
        date = datetime.strptime(k, "%Y-%m").date()
        if start <= date <= end:
            if isinstance(v, dict) and metric in v:  # For nested dictionaries in 'monthly_issue_stats' and 'monthly_pr_stats'
                relevant_data.append(v[metric])
            elif isinstance(v, int):  # Direct integer values in 'monthly_pr_comments'
                relevant_data.append(v)
    return sum(relevant_data) / len(relevant_data) if relevant_data else None



for index, row in df.iterrows():
    repo_name = row['listname']
    repo_status = 'graduated' if repo_name in data['graduated'] else 'retired'
    repo_data = data[repo_status].get(repo_name, {})

    # Get actual start and end dates from JSON data
    actual_start_str, actual_end_str = get_date_range_from_json(repo_data)
    if not actual_start_str or not actual_end_str:
        continue  # Skip this repo if no data available

    actual_start = datetime.strptime(actual_start_str, "%Y-%m").date()
    actual_end = datetime.strptime(actual_end_str, "%Y-%m").date()

    # Ensure that downturn dates are strings and valid
    downturn_start_str = row['downturn_start'] if isinstance(row['downturn_start'], str) else "NaT"
    downturn_end_str = row['downturn_end'] if isinstance(row['downturn_end'], str) else "NaT"

    if downturn_start_str == "NaT" or downturn_end_str == "NaT":
        print(f"Skipping repo {repo_name} due to missing downturn dates.")
        continue

    downturn_start = datetime.strptime(downturn_start_str, "%Y-%m").date()
    downturn_end = datetime.strptime(downturn_end_str, "%Y-%m").date()

    # Calculate metrics for each period
    for metric in metrics:
        if metric in['issue_average_close_time', 'num_issues']:
            metric_data = repo_data.get('monthly_issue_stats', {})
            # Check if the metric is one of the PR metrics
        elif metric in ['pr_ave_merge_time', 'ratio_mergedPR', 'num_merged_pr', 'num_open_pr', 'num_closed_pr']:
            metric_data = repo_data.get('monthly_pr_stats', {})
            # Check if the metric is 'monthly_pr_comments'
        elif metric == 'ave_pr_comments':
            metric_data = repo_data.get('monthly_pr_comments', {})

        for period in periods:
            col_name = f'{metric}_{period}'
            if period == 'pre_downturn':
                start, end = actual_start, downturn_start
            elif period == 'downturn':
                start, end = downturn_start, downturn_end
            else:
                start, end = downturn_end, actual_end

            average_metric = calculate_average_for_period(metric_data, start, end, metric)
            df.loc[index, col_name] = average_metric

# Save updated dataframe to Excel
output_excel_path = 'updated_excel.xlsx'
df.to_excel(output_excel_path, index=False)
print(f"Updated data saved to {output_excel_path}")



# Perform correlation analysis
def encode_graduated_status(status):
    return 1 if status == 'graduated' else 0

df['graduated_encoded'] = df['status'].apply(encode_graduated_status)

for metric in metrics:
    for period in periods:
        col_name = f'{metric}_{period}'
        # Create a mask for non-zero values
        non_zero_mask = df[col_name] != 0

        # Ensure there are more than one unique non-zero values for correlation
        if non_zero_mask.sum() > 1 and len(set(df[col_name][non_zero_mask])) > 1:
            correlation, p_value = pearsonr(df['graduated_encoded'][non_zero_mask], df[col_name][non_zero_mask])
            print(f'Correlation for {col_name}: {correlation} (p-value: {p_value})')
        else:
            print(f'Cannot compute correlation for {col_name} because there are not enough non-zero values.')



# 计算并打印相关系数
correlation, p_value = pearsonr(df['pr_ave_merge_time_post_downturn'].fillna(0), df['graduated_encoded'])
print(f'Correlation coefficient: {correlation}')
print(f'p-value: {p_value}')



import matplotlib.pyplot as plt
import seaborn as sns

# Set the style for seaborn plots
sns.set(style="whitegrid")

# Loop through the metrics and periods and create scatter plots
for metric in metrics:
    for period in periods:
        col_name = f'{metric}_{period}'
        non_zero_df = df[df[col_name] != 0]
        sns.scatterplot(x=non_zero_df[col_name], y=non_zero_df['graduated_encoded'])
        plt.title(f'Scatter Plot of {col_name} vs Graduated Status')
        plt.xlabel(col_name)
        plt.ylabel('Graduated Status (Encoded)')
        plt.show()

# Create a new DataFrame to store correlations and p-values
correlation_matrix = pd.DataFrame(index=metrics, columns=periods)

# Calculate correlations and store them
for metric in metrics:
    for period in periods:
        col_name = f'{metric}_{period}'
        # Filter out rows where the metric is zero before calculating correlation
        non_zero_df = df[df[col_name] != 0]
        # Ensure that we have more than one unique value for correlation to be defined
        if non_zero_df[col_name].nunique() > 1:
            correlation, p_value = pearsonr(non_zero_df['graduated_encoded'], non_zero_df[col_name])
            # Store the correlation if p-value is less than 0.05 (significant)
            correlation_matrix.at[metric, period] = correlation if p_value < 0.05 else None
        else:
            # If only one unique value, correlation is not defined
            correlation_matrix.at[metric, period] = None

# Plot a heatmap
sns.heatmap(correlation_matrix.astype(float), annot=True, fmt=".2f", cmap='coolwarm')
plt.title('Heatmap of Correlation Coefficients')
plt.show()
