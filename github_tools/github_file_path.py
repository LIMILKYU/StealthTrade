import requests
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# 확인할 파일 경로 (테스트할 파일 지정)
file_path = "webhook_server.py"  # 또는 문제가 발생하는 파일 이름

# GitHub API 엔드포인트 (파일 조회)
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# API 요청 실행
response = requests.get(url, headers=headers)

# 결과 확인
if response.status_code == 200:
    print(f"✅ 파일 '{file_path}'을(를) 성공적으로 가져왔습니다!")
    file_data = response.json()
    print(f"📌 파일 경로: {file_data['path']}")
else:
    print(f"🚨 GitHub API 요청 실패! 상태 코드: {response.status_code}, 응답: {response.text}")
