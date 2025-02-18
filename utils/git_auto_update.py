import os
import subprocess

def pull_latest_code():
    """GitHub에서 최신 코드 가져오기"""
    try:
        subprocess.run(["git", "pull"], check=True)
        return "✅ 최신 코드 업데이트 완료"
    except subprocess.CalledProcessError:
        return "❌ 코드 업데이트 실패"

if __name__ == "__main__":
    print(pull_latest_code())
