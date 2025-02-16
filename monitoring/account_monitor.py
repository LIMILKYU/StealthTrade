# 📌 계좌 잔고 및 포지션 실시간 추적
# P&L(손익) 추적
# 포지션 상태 자동 모니터링
# 잔고 변동 감지 후 경고 알림

import logging
from binance.client import Client

class AccountMonitor:
    def __init__(self, client: Client):
        self.client = client
        logging.basicConfig(level=logging.INFO)

    def get_balance(self):
        """ 계좌 잔고 조회 """
        account_info = self.client.get_account()
        balances = {b["asset"]: float(b["free"]) for b in account_info["balances"]}
        logging.info(f"💰 Account Balances: {balances}")
        return balances

    def get_open_positions(self):
        """ 현재 오픈된 포지션 조회 """
        positions = self.client.futures_account()["positions"]
        open_positions = [p for p in positions if float(p["positionAmt"]) != 0]
        logging.info(f"📈 Open Positions: {open_positions}")
        return open_positions

    def monitor_pnl(self):
        """ 실시간 손익(PnL) 모니터링 """
        positions = self.get_open_positions()
        total_pnl = sum(float(p["unrealizedProfit"]) for p in positions)
        logging.info(f"🔍 Total PnL: {total_pnl:.2f} USDT")
        return total_pnl

if __name__ == "__main__":
    client = Client("API_KEY", "API_SECRET")
    monitor = AccountMonitor(client)
    monitor.get_balance()
    monitor.get_open_positions()
    monitor.monitor_pnl()
