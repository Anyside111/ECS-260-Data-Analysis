from collections import defaultdict
import re
import requests
import pandas as pd
from datetime import datetime
import requests


GITHUB_API = 'https://api.github.com'

tokens =['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','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','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','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']
current_token_index = 0

def get_current_token():
    """获取当前使用的令牌"""
    global current_token_index
    return tokens[current_token_index]

def rotate_token():
    """更换下一个令牌"""
    global current_token_index
    current_token_index = (current_token_index + 1) % len(tokens)
    print(f"Switched to token: {tokens[current_token_index]}")


# 请求头
def get_headers():
    """动态获取请求头"""
    token = get_current_token()  # 获取当前token
    return {'Authorization': f'token {token}'}

# 获取issue平均解决时间的函数
def get_issues(repo, state):
    """
    获取在指定时间段内创建的Issues。
    """
    issues = []
    page = 1
    while True:
        issues_url = f"{GITHUB_API}/repos/{repo}/issues"
        params = {
            'state': state,
            'page': page,
            'per_page': 100  # 最大值
        }
        response = requests.get(issues_url, headers=get_headers(), params=params)
        response.raise_for_status()  # 确保请求成功
        page_data = response.json()
        if not page_data:
            break  # 如果没有数据，结束循环
        issues.extend(page_data)
        page += 1  # 前往下一页

    return issues


def calculate_issue_stats(issues):
    """
    计算Issues数量和平均关闭时间。
    """
    num_issues = len(issues)
    total_close_time = 0
    resolved_issues = 0

    for issue in issues:
        if 'closed_at' in issue and issue['closed_at']:
            created_at = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
            close_time = (closed_at - created_at).total_seconds()
            total_close_time += close_time
            resolved_issues += 1

    # 计算平均解决时间（以秒为单位），如果有已解决的问题
    if resolved_issues:
        issue_average_close_time = total_close_time / resolved_issues
    else:
        issue_average_close_time = 0

    return num_issues, issue_average_close_time / 3600  # 将平均解决时间转换为小时


# 示例使用
# repo = 'apache/DistributedLog'  # 仓库名称
# state = 'all'
# since = datetime(2013, 3, 1)  # 开始日期
# until = datetime(2013, 5, 31)  # 结束日期
# issues = get_issues(repo, 'closed', since, until)
# num_issues, issue_ave_close_time = calculate_issue_stats(issues)

def calculate_monthly_issue_stats(issues_by_month):
    """
       Calculate monthly stats for issues, including the number of open issues
       and the number of issues with 'good first issue' labels.
       """
    monthly_stats = {}
    good_label_pattern = re.compile(
        r'good first issue|beginners?|beginner friendly|contributions? welcome|help wanted|first pull request|first time contributor|good first pr',
        re.IGNORECASE)

    for month, issues in issues_by_month.items():
        num_issues, issue_ave_close_time = calculate_issue_stats(issues)
        num_open_issues = sum(1 for issue in issues if issue['state'] == 'open')
        num_good_first_issues = sum(1 for issue in issues if 'labels' in issue and any(
            good_label_pattern.search(label['name']) for label in issue['labels']))

        monthly_stats[month] = {
            'num_issues': num_issues,
            'issue_average_close_time': issue_ave_close_time,
            'num_open_issues': num_open_issues,
            'num_good_first_issues': num_good_first_issues,
        }
    return monthly_stats


# 获取PR信息的函数
def get_pull_requests(repo):
    """
    Fetch all pull requests in a given state and time period.
    """
    pull_requests = []
    page = 1
    while True:
        url = f"{GITHUB_API}/repos/{repo}/pulls"
        params = {
            'state': 'all',  # 'open', 'closed', or 'all'
            'per_page': 100,
            'page': page,
        }
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        prs = response.json()
        if not prs:
            break
        pull_requests.extend(prs)
        page += 1
    return pull_requests

def filter_data_by_date(data, since, until):
    """
    过滤在指定时间范围内创建的数据（issues或PRs）。
    """
    filtered_data = [item for item in data if since <= datetime.strptime(item['created_at'], "%Y-%m-%dT%H:%M:%SZ").date() <= until]
    return filtered_data

def group_prs_by_month(pull_requests):
    """
    Group pull requests by their creation month.
    """
    prs_by_month = defaultdict(list)
    for pr in pull_requests:
        created_at = datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        month_key = created_at.strftime('%Y-%m')
        prs_by_month[month_key].append(pr)
    return prs_by_month


def calculate_monthly_pr_stats(prs_by_month):
    """
    Calculate monthly PR stats from grouped PR data.
    """
    monthly_stats = {}
    for month, prs in prs_by_month.items():
        num_open_pr = sum(1 for pr in prs if pr['state'] == 'open')
        num_closed_pr = sum(1 for pr in prs if pr['state'] == 'closed')
        num_merged_pr = sum(1 for pr in prs if pr.get('merged_at'))
        total_merge_time = sum(
            (datetime.strptime(pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ") -
             datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
            for pr in prs if pr.get('merged_at')
        )
        pr_ave_merge_time = (total_merge_time / num_merged_pr) / 3600 if num_merged_pr else 0
        ratio_mergedPR = num_merged_pr / num_closed_pr if num_closed_pr else 0

        monthly_stats[month] = {
            'num_open_pr': num_open_pr,
            'num_closed_pr': num_closed_pr,
            'num_merged_pr': num_merged_pr,
            'ratio_mergedPR': ratio_mergedPR,
            'pr_ave_merge_time': pr_ave_merge_time,
        }
    return monthly_stats

# # Example usage
# repo = 'apache/DistributedLog'  # GitHub repo path
# all_pull_requests = get_pull_requests(repo)
# prs_by_month = group_prs_by_month(repo, all_pull_requests)
# monthly_pr_stats = calculate_monthly_pr_stats(repo, prs_by_month)
#
# for month, stats in monthly_pr_stats.items():
#     print(f"Month: {month}, Stats: {stats}")


# 获取PR评论信息的函数
def calculate_monthly_pr_comments(prs_by_month):
    """
    Calculate the total number of comments for PRs grouped by month.
    """
    monthly_comments_stats = {}

    for month, prs in prs_by_month.items():
        total_comments = 0
        for pr in prs:
            # 分别获取issue评论和代码审查评论的URL
            comments_url = pr['comments_url']
            review_comments_url = pr['_links']['review_comments']['href']

            # 获取issue评论数量
            comments_resp = requests.get(comments_url, headers=get_headers())
            comments_resp.raise_for_status()
            issue_comments = comments_resp.json()
            total_comments += len(issue_comments)

            # 获取代码审查评论数量
            review_comments_resp = requests.get(review_comments_url, headers=get_headers())
            review_comments_resp.raise_for_status()
            review_comments = review_comments_resp.json()
            total_comments += len(review_comments)

        # 存储每个月份的评论总数
        monthly_comments_stats[month] = total_comments

    return monthly_comments_stats

# # Example usage
# repo = 'apache/DistributedLog'  # GitHub repo path
# all_pull_requests = get_pull_requests(repo)
# prs_by_month = group_prs_by_month(all_pull_requests)
# # 计算每个月的PR评论统计数据
# monthly_pr_comments = calculate_monthly_pr_comments(prs_by_month)
#
# for month, total_comments in monthly_pr_comments.items():
#     print(f"Month: {month}, Total Comments: {total_comments}")


# Json格式化
import json

def fetch_repo_data(repo, since, until):
    """
    Fetch and analyze issues and pull requests data for a given repo, returning JSON-formatted results.
    """
    # 获取并分组Issues数据
    all_issues = get_issues(repo, 'all')
    filtered_issues = filter_data_by_date(all_issues, since, until)
    issues_by_month = group_prs_by_month(filtered_issues)  # 注意：这里复用了PR的分组函数，因为逻辑相同

    # 获取并分组PRs数据
    all_pull_requests = get_pull_requests(repo)
    filtered_pull_requests = filter_data_by_date(all_pull_requests, since, until)
    prs_by_month = group_prs_by_month(filtered_pull_requests)

    # 计算每个月的Issues统计数据
    monthly_issue_stats = calculate_monthly_issue_stats(issues_by_month)

    # 计算每个月的PRs统计数据
    monthly_pr_stats = calculate_monthly_pr_stats(prs_by_month)

    # 计算每个月的PR评论统计数据
    monthly_pr_comments = calculate_monthly_pr_comments(prs_by_month)

    # 组合数据
    results = {
        'repo': repo,
        'monthly_issue_stats': monthly_issue_stats,
        'monthly_pr_stats': monthly_pr_stats,
        'monthly_pr_comments': monthly_pr_comments,
    }

    # 转换为JSON格式并返回
    # return json.dumps(results, indent=2)
    return results




# 使用示例
# repo = 'apache/DistributedLog'  # GitHub repo path
# since = datetime(2017, 6, 24)  # 开始日期
# until = datetime(2017, 7, 1)  # 结束日期
#
# repo_data_json = fetch_repo_data(repo, since, until)
# print(repo_data_json)

def extract_first_repo(url):
    """从可能包含多个URL的字符串中提取第一个GitHub仓库名"""
    if isinstance(url, str):
        url = url.strip()
    else:
        return None
    first_url = url.split('|')[0].strip()  # 分割字符串并取第一个URL，同时去除空白符
    repo_name = '/'.join(first_url.split('/')[-2:]).replace('.git', '')  # 提取仓库名并去除.git
    return repo_name
    # if isinstance(repo_url, str):
    #     repo_url = repo_url.strip()
    #     # Split based on space and filter out any empty strings in case of multiple spaces
    #     urls = [url for url in repo_url.split(' ') if url]
    #     for url in urls:
    #         if 'github.com/' in url:
    #             # Find the index of 'github.com/' and extract from that index to the end
    #             start = url.find('github.com/') + len('github.com/')
    #             # Extract the repo path and remove any trailing '.git' or '/'
    #             repo_path = url[start:].split('/', 2)  # Limit to 2 splits to get user/repo format
    #             if len(repo_path) >= 2:
    #                 return '/'.join(repo_path[:2]).rstrip('.git').rstrip('/')
    # return None


import pandas as pd
import json
from datetime import datetime


# 假设fetch_repo_data已经修改为返回字典

def process_and_save_data(excel_path):
    df = pd.read_excel(excel_path)
    repo_count = 0
    # 初始化或加载已有的数据
    try:
        with open('New_proj_metrics.json', 'r') as file:
            all_data = json.load(file)
    except FileNotFoundError:
        all_data = {'graduated': {}, 'retired': {}}  # 初始化数据

    for index, row in df.iterrows():
        repo_url = row['pj_github_url']
        if pd.isnull(repo_url) or not isinstance(repo_url, str):
            continue  # 跳过这一行
        repo = extract_first_repo(repo_url)  # 处理可能的多个URL
        if repo:
            # 确保没有多余的斜杠或其他字符
            repo = repo.rstrip('/').replace('/issues', '')
        # since = datetime.strptime(row['start_date'][:10], '%Y-%m-%d').date()
        # until = datetime.strptime(row['end_date'][:10], '%Y-%m-%d').date()

        status_key = 'graduated' if row['status'] == 1 else 'retired' if row['status'] == 2 else 'unknown'

        since = row['start_date'].date()
        until = row['end_date'].date()

        # 检查是否已处理过该仓库
        if repo and repo not in all_data[status_key]:
            if repo_count % 1 == 0 and repo_count != 0:  # 每处理完两个仓库后更换token
                rotate_token()
            # 调用fetch_repo_data函数处理数据
            repo_data = fetch_repo_data(repo, since, until)

            # 将数据添加到all_data字典中
            all_data[status_key][repo] = repo_data

            # 立即将更新后的数据保存为JSON文件
            with open('New_proj_metrics.json', 'w') as file:
                json.dump(all_data, file, indent=2)
            print(f"Data for {repo} has been saved to New_proj_metrics.json")
            repo_count += 1

# 示例调用
excel_path = 'D:/ECS 260/add_issue_tag/asfi_list.xlsx'
process_and_save_data(excel_path)
# response = requests.get('https://api.github.com/rate_limit', headers={'Authorization': 'token YOUR_TOKEN'})
# print(response.json())
