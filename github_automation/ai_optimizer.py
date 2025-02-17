import openai

def optimize_code(code):
    openai.api_key = "your_openai_api_key"
    prompt = f"다음 코드를 최적화하고 가독성을 개선해 주세요:\n\n{code}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    print("🚀 AI 기반 코드 최적화 실행 중...")
    
    # 최적화할 코드 예제
    example_code = """
def sum_numbers(n):
    result = 0
    for i in range(n):
        result += i
    return result
"""
    
    optimized_code = optimize_code(example_code)
    print("🔹 최적화된 코드:\n", optimized_code)
