class AIControlMode:
    AUTOMATIC = "automatic"  # AI 100% 자동
    SEMI_AUTOMATIC = "semi_automatic"  # AI 보조 (분석만 수행, 매매는 수동)
    HYBRID = "hybrid"  # AI + 수동 혼합
    MANUAL = "manual"  # 수동 모드 (AI 개입 없음)

# 기본값 설정
ai_control_mode = AIControlMode.AUTOMATIC

def set_ai_control_mode(mode):
    global ai_control_mode
    if mode in [AIControlMode.AUTOMATIC, AIControlMode.SEMI_AUTOMATIC, AIControlMode.HYBRID, AIControlMode.MANUAL]:
        ai_control_mode = mode
        print(f"✅ AI 개입 모드가 {mode}로 변경되었습니다.")
    else:
        print("❌ 잘못된 모드 입력")
import telebot

# ✅ AI 개입 조절 기능 추가
class AIControlMode:
    AUTOMATIC = "automatic"  # AI 100% 자동
    SEMI_AUTOMATIC = "semi_automatic"  # AI 보조 (분석만 수행, 매매는 수동)
    HYBRID = "hybrid"  # AI + 수동 혼합
    MANUAL = "manual"  # 수동 모드 (AI 개입 없음)

# 기본값 설정
ai_control_mode = AIControlMode.AUTOMATIC

# ✅ 웹 대시보드 및 텔레그램에서 AI 개입 수준 조절 기능 추가
bot = telebot.TeleBot("YOUR_TELEGRAM_BOT_API_KEY")

def set_ai_control_mode(mode):
    global ai_control_mode
    if mode in [AIControlMode.AUTOMATIC, AIControlMode.SEMI_AUTOMATIC, AIControlMode.HYBRID, AIControlMode.MANUAL]:
        ai_control_mode = mode
        print(f"✅ AI 개입 모드가 {mode}로 변경되었습니다.")
    else:
        print("❌ 잘못된 모드 입력")

@bot.message_handler(commands=['set_ai_mode'])
def change_ai_mode(message):
    mode = message.text.split()[-1]  # 명령어 뒤의 옵션을 가져옴
    set_ai_control_mode(mode)
    bot.send_message(message.chat.id, f"AI 모드가 {ai_control_mode}로 변경되었습니다.")

# ✅ AI 개입 모드에 따른 매매 로직 분기 처리
def execute_trade_signal(signal):
    global ai_control_mode
    
    if ai_control_mode == AIControlMode.AUTOMATIC:
        execute_trade(signal)  # AI가 매매 결정 후 자동 실행

    elif ai_control_mode == AIControlMode.SEMI_AUTOMATIC:
        print(f"🟡 AI 분석 결과: {signal}, 사용자의 승인 필요")
        send_telegram_alert(f"AI 분석 결과: {signal}, 매매 승인 필요")
        
    elif ai_control_mode == AIControlMode.HYBRID:
        if signal.confidence > 0.8:  # 신뢰도가 높으면 자동 실행
            execute_trade(signal)
        else:
            print(f"🟡 신뢰도 낮음, 수동 확인 필요: {signal}")
            send_telegram_alert(f"신뢰도 낮음, 수동 확인 필요: {signal}")

    elif ai_control_mode == AIControlMode.MANUAL:
        print(f"🔴 수동 모드 - AI 개입 없음. 사용자가 직접 매매 결정해야 함")
        send_telegram_alert("수동 모드 - AI 개입 없음. 직접 매매 결정 필요")

# ✅ AI 개입 조절 기능을 분석 모드에도 반영
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

@bot.message_handler(commands=['set_analysis_mode'])
def change_analysis_mode(message):
    mode = message.text.split()[-1]
    set_analysis_mode(mode)
    bot.send_message(message.chat.id, f"분석 모드가 {analysis_mode}로 변경되었습니다.")

def analyze_market_data(data):
    global analysis_mode
    
    if analysis_mode == AnalysisMode.TRADITIONAL:
        return traditional_analysis(data)  # 재래식 분석 실행
    
    elif analysis_mode == AnalysisMode.AI_ASSISTED:
        ai_result = ai_analysis(data)
        print(f"🟡 AI 분석 결과 참고: {ai_result}")
        return traditional_analysis(data)
    
    elif analysis_mode == AnalysisMode.HYBRID:
        traditional_result = traditional_analysis(data)
        ai_result = ai_analysis(data)
        return combine_results(traditional_result, ai_result)
    
    elif analysis_mode == AnalysisMode.AI_ONLY:
        return ai_analysis(data)  # AI 100% 자동 분석

# 기존 코드 유지: 매매 실행 로직
def execute_trade(signal):
    print(f"🟢 매매 실행: {signal}")
    # 실행 로직 추가

def send_telegram_alert(message):
    bot.send_message("YOUR_TELEGRAM_CHAT_ID", message)

# 기존 분석 함수 유지
def traditional_analysis(data):
    print("📊 재래식 분석 수행")
    return "BUY"  # 예제

def ai_analysis(data):
    print("🤖 AI 분석 수행")
    return "SELL"  # 예제

def combine_results(traditional_result, ai_result):
    print("🔀 AI & 재래식 분석 결합")
    return traditional_result if traditional_result == ai_result else "HOLD"  # 예제

# 텔레그램 봇 실행
bot.polling()
