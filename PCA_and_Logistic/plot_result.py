import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 5-Fold Cross-Validation scores
folds = ['Fold 1', 'Fold 2', 'Fold 3', 'Fold 4', 'Fold 5']
scores = [0.72727273, 0.90909091, 0.81818182, 0.81818182, 0.72727273]

# Creating the bar chart
sns.set(style="whitegrid")
mean_accuracy = np.mean(scores)

plt.figure(figsize=(10, 6))
bars = plt.bar(folds, scores, color='skyblue', alpha=0.7)
plt.title('Model Predictive Performance: 5-Fold Cross-Validation', fontsize=18)
plt.xlabel('Fold', fontsize=18)
plt.ylabel('Accuracy', fontsize=18)
plt.ylim(0, 1)
plt.axhline(y=mean_accuracy, color='r', linestyle='-', label=f'Mean Accuracy: {mean_accuracy:.2f}')
plt.legend(fontsize=16)
plt.grid(True, axis='y')

plt.xticks(range(len(folds)), folds, fontsize=16)  # Set the fontsize for x-axis tick labels
plt.yticks(fontsize=16)  # Set the fontsize for y-axis tick labels
plt.tight_layout()
plt.show()

