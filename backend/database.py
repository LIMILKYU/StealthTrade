import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect("stealthtrade.db")
cursor = conn.cursor()

# 거래 기록 저장 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        order_type TEXT,
        price REAL,
        size REAL
    )
""")

def save_trade(timestamp, order_type, price, size):
    """ 거래 기록 저장 """
    cursor.execute("INSERT INTO trades (timestamp, order_type, price, size) VALUES (?, ?, ?, ?)", 
                   (timestamp, order_type, price, size))
    conn.commit()

def get_all_trades():
    """ 저장된 모든 거래 기록 조회 """
    cursor.execute("SELECT * FROM trades")
    return cursor.fetchall()

if __name__ == "__main__":
    # 예제 데이터 저장
    save_trade("2025-02-17 15:00:00", "buy", 45000.0, 0.01)
    print("📊 모든 거래 기록:", get_all_trades())
