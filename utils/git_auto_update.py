import os
import subprocess

def pull_latest_code():
    """GitHub에서 최신 코드 가져오기 (재시도 포함)"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = subprocess.run(["git", "pull"], check=True, capture_output=True, text=True)
            print(f"✅ 최신 코드 업데이트 완료:\n{result.stdout}")
            return "✅ 최신 코드 업데이트 완료"
        except subprocess.CalledProcessError as e:
            print(f"❌ 코드 업데이트 실패 [{attempt+1}/{max_retries}] 재시도 중...\n{e.stderr}")
    
    print("🚨 업데이트 실패: GitHub 접근 오류")
    return "🚨 업데이트 실패: GitHub 접근 오류"

if __name__ == "__main__":
    pull_latest_code()
