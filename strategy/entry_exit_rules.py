import numpy as np

def calculate_bid_ask_imbalance(order_book):
    """
    Bid-Ask Imbalance 계산
    order_book: {'bids': [(price, size), ...], 'asks': [(price, size), ...]}
    """
    bid_volume = sum([size for _, size in order_book['bids']])
    ask_volume = sum([size for _, size in order_book['asks']])
    imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
    return imbalance

def calculate_trade_intensity(trade_data, window=10):
    """
    체결 강도 계산 (최근 window 개의 체결 데이터 평균)
    trade_data: [{'price': x, 'size': y, 'side': 'buy' or 'sell'}, ...]
    """
    if len(trade_data) < window:
        return None
    
    buy_volume = sum([trade['size'] for trade in trade_data[-window:] if trade['side'] == 'buy'])
    sell_volume = sum([trade['size'] for trade in trade_data[-window:] if trade['side'] == 'sell'])
    return (buy_volume - sell_volume) / (buy_volume + sell_volume)

def detect_iceberg_orders(order_book, threshold=0.2):
    """
    Iceberg 주문 감지 (작은 주문이 반복적으로 나오면 감지)
    order_book: {'bids': [(price, size), ...], 'asks': [(price, size), ...]}
    """
    small_orders = [size for _, size in order_book['bids'] if size < threshold] + \
                   [size for _, size in order_book['asks'] if size < threshold]
    return len(small_orders) > 5

def calculate_obv(price_series, volume_series):
    """
    OBV (On-Balance Volume) 계산
    price_series: 가격 데이터 리스트
    volume_series: 거래량 데이터 리스트
    """
    obv = [0]
    for i in range(1, len(price_series)):
        if price_series[i] > price_series[i-1]:
            obv.append(obv[-1] + volume_series[i])
        elif price_series[i] < price_series[i-1]:
            obv.append(obv[-1] - volume_series[i])
        else:
            obv.append(obv[-1])
    return obv[-1]

def calculate_vwap(prices, volumes):
    """
    VWAP (거래량 가중 평균가) 계산
    """
    cumulative_vp = np.cumsum(np.array(prices) * np.array(volumes))
    cumulative_volume = np.cumsum(volumes)
    return cumulative_vp / cumulative_volume

def calculate_atr(high_prices, low_prices, close_prices, window=14):
    """
    ATR (평균 진폭) 계산
    """
    tr = [max(high - low, abs(high - close), abs(low - close)) for high, low, close in zip(high_prices, low_prices, close_prices)]
    atr = np.mean(tr[-window:])
    return atr

def generate_trade_signal(order_book, trade_data, price_series, volume_series, high_prices, low_prices, close_prices):
    """
    매매 신호 생성 (Bid-Ask Imbalance + 체결 강도 + OBV + VWAP + ATR 조합)
    """
    imbalance = calculate_bid_ask_imbalance(order_book)
    trade_intensity = calculate_trade_intensity(trade_data)
    iceberg_detected = detect_iceberg_orders(order_book)
    obv = calculate_obv(price_series, volume_series)
    vwap = calculate_vwap(price_series, volume_series)
    atr = calculate_atr(high_prices, low_prices, close_prices)
    
    if imbalance > 0.2 and trade_intensity > 0.1 and obv > 0 and price_series[-1] > vwap and atr > np.mean(atr):
        return "BUY"
    elif imbalance < -0.2 and trade_intensity < -0.1 and obv < 0 and price_series[-1] < vwap and atr > np.mean(atr):
        return "SELL"
    return "HOLD"
