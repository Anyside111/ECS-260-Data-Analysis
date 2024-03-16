import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_recall_curve

# read data
file_path = 'updated_excel_final.xlsx'
df = pd.read_excel(file_path)

metrics = ['num_issues', 'issue_average_close_time', 'pr_ave_merge_time', 'ratio_mergedPR',
           'num_merged_pr', 'num_open_pr', 'num_closed_pr', 'ave_pr_comments'
           ] #,'changes_per_commit', 'avg_monthly_commit'
periods = ['pre_downturn', 'downturn', 'post_downturn']
feature_columns = [f'{metric}_{period}' for metric in metrics for period in periods]
y = df['status'].values

# only select existing columns
df_selected = df[feature_columns]

# data preprocessing
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
df_filled = imputer.fit_transform(df_selected)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_filled)

# feature selection
forest = RandomForestClassifier(n_estimators=100, random_state=42)
forest.fit(X_scaled, y)
model = SelectFromModel(forest, prefit=True)
X_selected = model.transform(X_scaled)
print(f"Selected {X_selected.shape[1]} features from the original {df_filled.shape[1]} features.")

# apply PCA
pca = PCA().fit(X_selected)

# determine the number of components needed to explain 80% variance
cumulative_variance_ratio = np.cumsum(pca.explained_variance_ratio_)
n_components = np.where(cumulative_variance_ratio >= 0.8)[0][0] + 1
print(f"Number of components to explain 80% variance: {n_components}")

# run PCA again with the determined number of principal components
pca_final = PCA(n_components=n_components)
X_pca_final = pca_final.fit_transform(X_selected)
explained_variance_ratio_final = pca_final.explained_variance_ratio_

print(f"Selected {n_components} principal components.")
print("Explained variance ratio by selected components:", explained_variance_ratio_final)

# print the linear combination formulae of principal components
print("Principal Components' Linear Combination Formulae:")
for i, component in enumerate(pca_final.components_, start=1):
    formula = ' + '.join(f"{coef:.3f}*{feature}" for coef, feature in zip(component, np.array(feature_columns)[model.get_support()]))
    print(f"PC{i}: {formula}")

X_train, X_test, y_train, y_test = train_test_split(X_pca_final, y, test_size=0.2, random_state=42)

# Use SMOTE to oversample the minority class in the training data
smote = SMOTE(random_state=42)
X_sm, y_sm = smote.fit_resample(X_train, y_train)

# # The first model: Random Forest classifier
# forest_model = RandomForestClassifier(n_estimators=100, random_state=42)
#
# # Train the model using the oversampled data
# forest_model.fit(X_sm, y_sm)
#
# # Evaluate the model on the test set
# y_pred = forest_model.predict(X_test)
# print(classification_report(y_test, y_pred))
#
# # Calculate the precision and recall for the precision-recall curve
# y_scores_forest = forest_model.predict_proba(X_test)[:, 1]
# precision_forest, recall_forest, _ = precision_recall_curve(y_test, y_scores_forest)
#
# # Plot the precision-recall curve
# plt.figure(figsize=(10, 6))
# plt.plot(recall_forest, precision_forest, marker='.', label='Random Forest', color='forestgreen')
# plt.xlabel('Recall', fontsize=16)
# plt.ylabel('Precision', fontsize=16)
# plt.title('Precision-Recall Curve of Random Forest classifier', fontsize=20)
# plt.legend(fontsize=14)
# plt.xticks(fontsize=14)
# plt.yticks(fontsize=14)
# plt.tight_layout()
# plt.show()


# The second model: logistic regression model
logistic_model = LogisticRegression()

# train the model
logistic_model.fit(X_pca_final, y)
print("Intercept (model bias):", logistic_model.intercept_)
print("Coefficients (model weights):", logistic_model.coef_)

# visualize the coefficients
features = [f"PC{i+1}" for i in range(n_components)]
coef = logistic_model.coef_[0]

plt.figure(figsize=(10, 6))
bars = plt.bar(features, coef, color='steelblue', alpha=0.7)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom', fontsize=15)

plt.title('Logistic Regression Coefficients of Logistic Model' , fontsize=16)
plt.xlabel('Principal Components', fontsize=16)
plt.ylabel('Coefficient Value', fontsize=16)
plt.xticks(ticks=np.arange(len(features)), labels=features, rotation=45, fontsize=14)
plt.yticks(fontsize=14)
plt.tight_layout()
plt.show()

# k-fold cross-validation
cv_scores = cross_val_score(logistic_model, X_pca_final, y, cv=5)
print(f"Cross-validation scores: {cv_scores}")
print(f"Mean CV score: {np.mean(cv_scores)}")

# precision-recall curve
y_scores = logistic_model.predict_proba(X_pca_final)[:, 1]
precision, recall, thresholds = precision_recall_curve(y, y_scores)

# plot the precision-recall curve
plt.figure(figsize=(10, 6))
plt.plot(recall, precision, marker='.', label='Logistic Regression', color='#2ca02c')  # A nice shade of green
plt.xlabel('Recall', fontsize=18)
plt.ylabel('Precision', fontsize=18)
plt.title('Precision-Recall Curve of Logistic Model', fontsize=18)
plt.legend(fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
plt.show()
