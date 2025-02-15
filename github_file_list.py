import os
import time
import requests
import base64
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# GitHub API 요청 URL
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# API 호출하여 저장소 파일 목록 가져오기
response = requests.get(url, headers=headers)

if response.status_code == 200:
    files = response.json()
    print("✅ 저장소 내 파일 목록:")
    for file in files:
        print(file["path"])  # 파일 전체 경로 출력
else:
    print(f"🚨 GitHub API 요청 실패! 상태 코드: {response.status_code}, 응답: {response.text}")
