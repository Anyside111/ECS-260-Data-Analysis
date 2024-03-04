# ECS-260-Data-Analysis

## Overview
This project is focused on analyzing data related to Pull Requests (PR) and issue activities within a selected set of projects stored in the 'ASFI List_reduced.xlsx' file. Through the use of the GitHub API, we capture all the relevant metrics and analyze the correlation of data to understand trends and patterns.

## Files Description
- **ASFI List_reduced.xlsx**: Contains the initial list of selected projects for analysis.
- **monthly_data.py**: A script to capture metrics related to PR and issue activities from the GitHub API. The output is stored in a JSON file named 'issue_and_PR_metrics.json'.
- **data_preprocessing.py**: This script preprocesses the data from 'issue_and_PR_metrics.json' and calculates the monthly average metrics. The results are written back to the 'ASFI List_reduced.xlsx' file.
- **ECS_260_Analysis.ipynb**: A Jupyter notebook used for analyzing the correlation of data from the 'ASFI List_reduced.xlsx' file. It provides insights into the patterns and trends of PR and issue activities across the selected projects.

## Getting Started
To get started with this analysis, follow the steps below:

1. **Setup**: Ensure you have Python installed on your system. The analysis requires Python 3.x.

2. **Install Dependencies**: Install the necessary Python packages by running the following command:

3. **Run the Scripts**:
- To capture and store the metrics, run:
  ```
  python monthly_data.py
  ```
- To preprocess the data and calculate the monthly averages, run:
  ```
  python data_preprocessing.py
  ```
- To perform the analysis, open the `ECS_260_Analysis.ipynb` notebook in Jupyter and follow the instructions within.

## Contribution
Contributions to this project are welcome. To contribute, please fork the repository, make your changes, and submit a pull request.





