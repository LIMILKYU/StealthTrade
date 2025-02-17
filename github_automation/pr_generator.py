import requests

GITHUB_TOKEN = "your_github_token"
REPO_OWNER = "LIMILKYU"
REPO_NAME = "StealthTrade_Manager"
BRANCH_NAME = "feature-ai-optimization"

def create_pull_request():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    payload = {
        "title": "AI 코드 최적화 적용",
        "head": BRANCH_NAME,
        "base": "main",
        "body": "AI가 최적화한 코드입니다. 코드 리뷰 후 병합해주세요."
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("✅ PR 생성 성공!")
    else:
        print("❌ PR 생성 실패:", response.json())

if __name__ == "__main__":
    create_pull_request()
