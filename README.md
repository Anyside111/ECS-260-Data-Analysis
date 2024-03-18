# ECS260 Project group 19

## Overview
This repository contains the code and methodology for analyzing the factors contributing to the successful recovery of projects from downturns using Principal Component Analysis (PCA) and Logistic Regression.

## Repository Structure

- `PCA_and_Logistic`: Contains the PCA and Logistic Regression scripts for the analysis.
- `PR_and_issue_metric`: Scripts for collecting and calculating 12 metrics across 3 time windows for each project.
- `Tokei_metrics_automation`: Automation scripts for retrieving code metrics using Tokei.
- `add_issue_tag`: Scripts for adding issue tags and analyzing keywords in issues tag.
- `identify_downturns`: Scripts for identifying downturn periods in project activity.

## Scripts Description

### `PCA_and_Logistic`
This directory contains the final scripts for conducting PCA to reduce the dimensionality of the project metrics and applying Logistic Regression to predict the likelihood of project recovery.

### `PR_and_issue_metric`
Scripts in this directory calculate various metrics related to Pull Requests (PRs) and issues, providing insights into project activity levels during different phases of the project lifecycle.

### `Tokei_metrics_automation`
This contains scripts that automate the retrieval of code metrics using Tokei, a program that allows you to quickly get an overview of the codebase.

### `add_issue_tag`
Scripts here analyze issues for keyword tags, which can help in categorizing and understanding the types of problems projects encounter.

### `identify_downturns`
The scripts in this directory are used to identify periods of reduced activity, referred to as downturns, which can signal potential problems or areas where projects may struggle.

## Getting Started

To use the scripts and perform the analysis, follow the instructions below:

1. Ensure you have Python installed on your system, as the analysis requires Python 3.x.
2. Install all dependencies as mentioned in `requirements.txt`.
3. Execute the scripts in the order specified by the directory structure, starting with `PR_and_issue_metric` to gather the necessary metrics before moving on to `PCA_and_Logistic`.

## Data Analysis Workflow

The analysis workflow is as follows:

1. Run the metrics calculation scripts in `PR_and_issue_metric`.
2. Use the `Tokei_metrics_automation` scripts to supplement the metrics with additional codebase insights.
3. Apply the `add_issue_tag` script to incorporate issue tag analysis into the data.
4. Identify key periods of downturns using the `identify_downturns` script.
5. Finally, run the `PCA_and_Logistic` scripts to conduct PCA and Logistic Regression, predicting the recovery of projects.

## Contribution

We welcome contributions to improve the analysis. Please fork the repository and submit pull requests with your suggested changes.

