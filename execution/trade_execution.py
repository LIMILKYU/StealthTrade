import logging
from config.ai_control import ai_control_mode, AIControlMode
from execution.order_executor import place_order
from notification.telegram_notifier import send_telegram_alert

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_trade_signal(signal):
    """ AI 자동매매 모드에 따라 거래 실행 """
    global ai_control_mode

    if ai_control_mode == AIControlMode.AUTOMATIC:
        logger.info(f"🟢 [AI 자동매매] 실행: {signal}")
        execute_trade(signal)

    elif ai_control_mode == AIControlMode.SEMI_AUTOMATIC:
        logger.warning(f"🟡 [AI 분석] 신호 감지: {signal} → 사용자 승인 필요")
        send_telegram_alert(f"AI 분석 결과: {signal}, 매매 승인 필요")

    elif ai_control_mode == AIControlMode.HYBRID:
        if signal.confidence > 0.8:
            logger.info(f"🟢 [HYBRID] 높은 신뢰도 ({signal.confidence}) → 자동 실행")
            execute_trade(signal)
        else:
            logger.warning(f"🟡 [HYBRID] 신뢰도 낮음 ({signal.confidence}) → 수동 확인 필요")
            send_telegram_alert(f"신뢰도 낮음, 수동 확인 필요: {signal}")

    elif ai_control_mode == AIControlMode.MANUAL:
        logger.error(f"🔴 [MANUAL] 수동 모드 - AI 개입 없음")
        send_telegram_alert("수동 모드 - AI 개입 없음. 직접 매매 결정 필요")

def execute_trade(signal):
    """ ✅ 매매 실행 함수 (실제 주문 실행) """
    try:
        order_response = place_order(signal.symbol, signal.order_type, signal.quantity, "MARKET")
        logger.info(f"✅ [주문 성공] {order_response}")
        send_telegram_alert(f"✅ {signal.symbol} {signal.order_type} 주문 완료")
        return order_response
    except Exception as e:
        logger.error(f"🚨 [주문 실패] {e}")
        send_telegram_alert(f"🚨 {signal.symbol} {signal.order_type} 주문 실패")
        return None
