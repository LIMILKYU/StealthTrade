import os
import requests

# 환경 변수에서 GitHub 토큰 가져오기
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "LIMILKYU")
REPO_NAME = os.getenv("REPO_NAME", "CryptoTrade")

# API 요청 헤더 설정
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# Pull Request 생성 API URL
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"

# PR 생성 데이터
data = {
    "title": "자동 생성된 PR",
    "head": "main",
    "base": "main",
    "body": "이 PR은 자동으로 생성되었습니다. 확인 후 병합하세요.",
}

# PR 요청 보내기
response = requests.post(url, json=data, headers=headers)

# 결과 출력
if response.status_code == 201:
    print("[SUCCESS] PR 생성 완료 ✅")
    print(response.json().get("html_url"))
else:
    print("[ERROR] PR 생성 실패 ❌")
    print(response.json())
