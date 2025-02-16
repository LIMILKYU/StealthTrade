import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 생성
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 사용 가능한 모델 목록 조회
try:
    models = client.models.list()
    print("\n✅ 사용 가능한 OpenAI 모델 목록:")
    for model in models.data:
        print(f"- {model.id}")
except openai.OpenAIError as e:
    print(f"\n🚨 OpenAI API 오류 발생: {e}")
