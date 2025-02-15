from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
import requests
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 GitHub Token 및 OpenAI API Key 불러오기
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# GitHub API 요청 헤더 설정
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_pull_requests():
    """GitHub에서 열려있는 PR 목록을 가져옴"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_diff(pr_number):
    """특정 PR의 변경된 코드(diff)를 가져옴"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers)
    return response.json()

def generate_review(comments):
    """ChatGPT API를 사용하여 코드 리뷰 생성"""
    prompt = f"다음 코드 변경 사항을 리뷰해 주세요:\n\n{comments}"

      # OpenAI API 키 설정

    response = client.chat.completions.create(model="gpt-4",
    messages=[{"role": "system", "content": "You are a code reviewer."},
              {"role": "user", "content": prompt}])

    return response.choices[0].message.content

def post_review(pr_number, review_comments):
    """GitHub PR에 ChatGPT가 생성한 리뷰를 등록"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/comments"
    payload = {"body": review_comments}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 실행
if __name__ == "__main__":
    prs = fetch_pull_requests()
    if prs:
        for pr in prs:
            pr_number = pr["number"]
            print(f"[INFO] PR #{pr_number} 리뷰 진행 중...")

            diff = fetch_diff(pr_number)
            diff_text = "\n".join([file["patch"] for file in diff if "patch" in file])

            if diff_text:
                review_comments = generate_review(diff_text)
                post_review(pr_number, review_comments)
                print(f"[SUCCESS] PR #{pr_number} 리뷰 완료 ✅")
            else:
                print(f"[WARNING] PR #{pr_number}에 변경 사항이 없음.")
    else:
        print("[INFO] 리뷰할 PR이 없습니다.")
