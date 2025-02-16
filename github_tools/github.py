import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# GitHub 리포지토리 파일 목록 가져오기
def list_repository_files():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        files = response.json()
        for file in files:
            print(f"- {file['name']} ({file['path']})")
    else:
        print(f"[ERROR] GitHub 접속 실패: {response.status_code}")

# 실행
if __name__ == "__main__":
    list_repository_files()
