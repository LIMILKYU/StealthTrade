import os
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
import requests
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# OpenAI API 설정

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# GitHub에서 특정 파일 내용 가져오기
def get_github_file_content(file_path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        file_content = response.json().content
        return file_content
    else:
        print(f"[ERROR] {file_path} 다운로드 실패: {response.status_code}")
        return None

# ChatGPT를 활용한 코드 리뷰 요청
def review_code(file_path):
    file_content = get_github_file_content(file_path)

    if not file_content:
        return None

    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an AI code reviewer."},
        {"role": "user", "content": f"Review this code and suggest improvements:\n\n{file_content}"}
    ])

    return response.choices[0].message.content

# 실행
if __name__ == "__main__":
    file_path = "main.py"
    review_result = review_code(file_path)

    if review_result:
        print(f"\n🔍 **{file_path} 코드 리뷰 결과:**\n{review_result}\n")
    else:
        print(f"[ERROR] {file_path} 코드 리뷰 실패.")
