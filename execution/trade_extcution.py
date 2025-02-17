from config.ai_control import ai_control_mode, AIControlMode

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

def execute_trade(signal):
    print(f"🟢 매매 실행: {signal}")
    # 매매 실행 로직 추가

def send_telegram_alert(message):
    print(f"📩 텔레그램 알림: {message}")
