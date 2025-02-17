from trade import place_order
from telegram_alert import send_telegram_message

if __name__ == "__main__":
    send_telegram_message("📢 StealthTrader 자동매매 시작!")
    
    # ✅ 매수 주문 실행
    place_order(order_type="BUY")
    
    # ✅ 주문 성공 메시지 전송
    send_telegram_message("✅ 매매 성공! BTCUSDT 매수 완료!")
