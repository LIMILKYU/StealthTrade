import logging
import os
from dotenv import load_dotenv
from backend.t_rpc_client import tRPCClient
from notification.telegram_notifier import TelegramNotifier

# 환경 변수 로드
load_dotenv()

class DynamicStopLoss:
    def __init__(self, stop_loss_pct=2, take_profit_pct=5):
        """
        자동 손절 및 익절 시스템
        :param stop_loss_pct: 손절 기준 (%)
        :param take_profit_pct: 익절 기준 (%)
        """
        self.stop_loss_pct = stop_loss_pct  # 손절 기준 (예: 2%)
        self.take_profit_pct = take_profit_pct  # 익절 기준 (예: 5%)
        self.trpc_client = tRPCClient(os.getenv("TRPC_API_URL"))
        self.telegram_notifier = TelegramNotifier(
            os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        )
        logging.basicConfig(level=logging.INFO)

    def check_stop_loss(self, entry_price, current_price):
        """ 현재 가격이 손절 기준에 도달했는지 확인 """
        loss_percent = ((current_price - entry_price) / entry_price) * 100
        if loss_percent <= -self.stop_loss_pct:
            logging.warning(f"🚨 손절 기준 도달! 현재 손실: {loss_percent:.2f}%")
            self.telegram_notifier.send_message(f"🚨 손절 실행: {loss_percent:.2f}% 손실 발생")

            # tRPC API를 통해 손절 데이터 업데이트
            self.trpc_client.update_trade_data({
                "status": "STOP_LOSS_TRIGGERED",
                "loss_percent": loss_percent,
            })
            return True
        return False

    def check_take_profit(self, entry_price, current_price):
        """ 현재 가격이 익절 기준에 도달했는지 확인 """
        profit_percent = ((current_price - entry_price) / entry_price) * 100
        if profit_percent >= self.take_profit_pct:
            logging.info(f"✅ 익절 실행! 현재 수익: {profit_percent:.2f}%")
            self.telegram_notifier.send_message(f"✅ 익절 실행: {profit_percent:.2f}% 수익 달성")

            # tRPC API를 통해 익절 데이터 업데이트
            self.trpc_client.update_trade_data({
                "status": "TAKE_PROFIT_TRIGGERED",
                "profit_percent": profit_percent,
            })
            return True
        return False

# 사용 예시
if __name__ == "__main__":
    stop_loss_system = DynamicStopLoss(stop_loss_pct=2, take_profit_pct=5)
    
    # 테스트 데이터 (진입 가격 45000, 현재 가격 44000 → 손절 트리거)
    stop_loss_system.check_stop_loss(45000, 44000)

    # 테스트 데이터 (진입 가격 45000, 현재 가격 47500 → 익절 트리거)
    stop_loss_system.check_take_profit(45000, 47500)
