import requests
from config import HEADERS, REPO_OWNER, REPO_NAME

# GitHub API URL
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"

# API 요청
response = requests.get(url, headers=HEADERS)

if response.status_code == 200:
    files = response.json()
    
    # .py 파일만 필터링
    py_files = [file["name"] for file in files if file["name"].endswith(".py")]

    if py_files:
        print(f"[INFO] 분석 가능한 Python 파일 목록: {py_files}")
    else:
        print("[WARNING] 리포지토리에 Python 파일이 없습니다. main.py를 추가하세요.")
else:
    print(f"[ERROR] 파일 목록 불러오기 실패: {response.status_code}")
    print(response.json())
