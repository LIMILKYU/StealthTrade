import requests
import os
import base64

# 환경변수에서 GitHub 토큰 로드
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "LIMILKYU")
REPO_NAME = os.getenv("REPO_NAME", "CryptoTrade")

# 파일 정보
FILE_PATH = "README.md"  # 업데이트할 파일
BRANCH = "main"
COMMIT_MESSAGE = "Update README.md via API"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 1️⃣ 기존 파일 정보 가져오기 (SHA 값 필요)
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    file_data = response.json()
    sha = file_data["sha"]  # 기존 파일의 SHA 값
else:
    print(f"[ERROR] 파일을 찾을 수 없음: {response.status_code}")
    print(response.json())
    exit(1)

# 2️⃣ Base64로 인코딩하여 새로운 내용 준비
new_content = "## StealthTrader 🚀\nAI 기반 자동매매 시스템 - 업데이트됨!"
encoded_content = base64.b64encode(new_content.encode()).decode()

# 3️⃣ 파일 업데이트 요청
update_data = {
    "message": COMMIT_MESSAGE,
    "content": encoded_content,  # ✅ Base64 인코딩된 내용
    "sha": sha,  # 기존 SHA 값 필요
    "branch": BRANCH
}

response = requests.put(url, json=update_data, headers=headers)

# 4️⃣ 결과 확인
if response.status_code == 200:
    print("[SUCCESS] 파일 업데이트 성공 ✅")
else:
    print(f"[ERROR] 파일 업데이트 실패: {response.status_code}")
    print(response.json())  # 오류 메시지 출력
