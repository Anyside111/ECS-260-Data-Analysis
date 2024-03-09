import pandas as pd
import json
from datetime import datetime
from scipy.stats import pearsonr


# Load the Excel file
excel_path = 'asfi_list.xlsx'
df = pd.read_excel(excel_path)
df = pd.read_excel(excel_path, converters={
    # 'downturn_start': str,  # Convert downturn_start to string
    # 'downturn_end': str,    # Convert downturn_end to string
    'start_date': str,       # Convert start_date to string
    'end_date': str          # Convert end_date to string
})

# Load the JSON file
json_path = 'New_proj_metrics.json'
with open(json_path, 'r') as file:
    data = json.load(file)

# Add new columns to the DataFrame for the metrics
metrics = ['num_issues','issue_average_close_time', 'num_open_issues','num_good_first_issues','pr_ave_merge_time', 'ratio_mergedPR','num_merged_pr', 'num_open_pr', 'num_closed_pr', 'ave_pr_comments']
periods = ['lifecycle']

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

def extract_first_repo(url):
    """从可能包含多个URL的字符串中提取第一个GitHub仓库名"""
    if isinstance(url, str):
        url = url.strip()
    else:
        return None
    first_url = url.split('|')[0].strip()  # 分割字符串并取第一个URL，同时去除空白符
    repo_name = '/'.join(first_url.split('/')[-2:]).replace('.git', '')  # 提取仓库名并去除.git
    return repo_name

for index, row in df.iterrows():
    repo_url = row['pj_github_url']
    if pd.isnull(repo_url) or not isinstance(repo_url, str):
        continue  # 跳过这一行
    repo_name = extract_first_repo(repo_url)  # 处理可能的多个URL
    if repo_name:
        # 确保没有多余的斜杠或其他字符
        repo_name = repo_name.rstrip('/').replace('/issues', '')

    repo_status = 'graduated' if repo_name in data['graduated'] else 'retired'
    repo_data = data[repo_status].get(repo_name, {})

    # Get actual start and end dates from JSON data
    actual_start_str, actual_end_str = get_date_range_from_json(repo_data)
    if not actual_start_str or not actual_end_str:
        continue  # Skip this repo if no data available

    actual_start = datetime.strptime(actual_start_str, "%Y-%m").date()
    actual_end = datetime.strptime(actual_end_str, "%Y-%m").date()

    # Ensure that downturn dates are strings and valid
    # downturn_start_str = row['downturn_start'] if isinstance(row['downturn_start'], str) else "NaT"
    # downturn_end_str = row['downturn_end'] if isinstance(row['downturn_end'], str) else "NaT"
    #
    # if downturn_start_str == "NaT" or downturn_end_str == "NaT":
    #     print(f"Skipping repo {repo_name} due to missing downturn dates.")
    #     continue
    #
    # downturn_start = datetime.strptime(downturn_start_str, "%Y-%m").date()
    # downturn_end = datetime.strptime(downturn_end_str, "%Y-%m").date()

    # Calculate metrics for each period
    for metric in metrics:
        if metric in['issue_average_close_time', 'num_issues', 'num_open_issues','num_good_first_issues']:
            metric_data = repo_data.get('monthly_issue_stats', {})
            # Check if the metric is one of the PR metrics
        elif metric in ['pr_ave_merge_time', 'ratio_mergedPR', 'num_merged_pr', 'num_open_pr', 'num_closed_pr']:
            metric_data = repo_data.get('monthly_pr_stats', {})
            # Check if the metric is 'monthly_pr_comments'
        elif metric == 'ave_pr_comments':
            metric_data = repo_data.get('monthly_pr_comments', {})

        for period in periods:
            col_name = f'{metric}_{period}'
            if period == 'lifecycle':
                start, end = actual_start, actual_end
            # elif period == 'downturn':
            #     start, end = downturn_start, downturn_end
            # else:
            #     start, end = downturn_end, actual_end

            average_metric = calculate_average_for_period(metric_data, start, end, metric)
            df.loc[index, col_name] = average_metric

# Save updated dataframe to Excel
output_excel_path = 'updated_excel.xlsx'
df.to_excel(output_excel_path, index=False)
print(f"Updated data saved to {output_excel_path}")



