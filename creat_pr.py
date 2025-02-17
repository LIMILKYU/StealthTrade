import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "LIMILKYU"
REPO_NAME = "StealthTrade"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"

data = {
    "title": "🔄 자동 생성된 PR",
    "head": "feature-auto-update",
    "base": "main",
    "body": "이 PR은 자동으로 생성되었으며, 코드 검토 후 병합 바랍니다.",
    "reviewers": ["LIMILKYU"]  # 자동으로 리뷰어 지정
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("✅ PR 생성 완료!", response.json().get("html_url"))
else:
    print("❌ PR 생성 실패!", response.json())
