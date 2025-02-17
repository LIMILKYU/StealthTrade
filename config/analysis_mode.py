class AnalysisMode:
    TRADITIONAL = "traditional"  # 재래식 분석
    AI_ASSISTED = "ai_assisted"  # AI 보조 분석 (참고만)
    HYBRID = "hybrid"  # 재래식 분석 + AI 분석 결합
    AI_ONLY = "ai_only"  # AI 100% 자동 분석

# 기본 분석 모드 설정
analysis_mode = AnalysisMode.TRADITIONAL

def set_analysis_mode(mode):
    global analysis_mode
    if mode in [AnalysisMode.TRADITIONAL, AnalysisMode.AI_ASSISTED, AnalysisMode.HYBRID, AnalysisMode.AI_ONLY]:
        analysis_mode = mode
        print(f"✅ 분석 모드가 {mode}로 변경되었습니다.")
    else:
        print("❌ 잘못된 모드 입력")
