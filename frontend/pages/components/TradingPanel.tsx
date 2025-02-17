import React, { useState } from "react";
import { trpc } from "../utils/trpc";

export default function TradingPanel() {
    const [symbol, setSymbol] = useState("BTCUSDT");
    const [quantity, setQuantity] = useState(0.01);

    const handleTrade = async (orderType: string) => {
        await trpc.trading.place_order.mutate({ orderType, symbol, quantity });
        alert(`🚀 ${orderType} ${symbol} 주문 실행!`);
    };

    return (
        <div>
            <h2>📈 트레이딩 패널</h2>
            <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
                <option value="BTCUSDT">BTC/USDT</option>
                <option value="ETHUSDT">ETH/USDT</option>
            </select>
            <input type="number" value={quantity} onChange={(e) => setQuantity(parseFloat(e.target.value))} />
            <button onClick={() => handleTrade("BUY")}>매수</button>
            <button onClick={() => handleTrade("SELL")}>매도</button>
        </div>
    );
}
