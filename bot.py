import os
import time
import ccxt
import pandas as pd
import pandas_ta as ta
from flask import Flask

app = Flask(__name__)

exchange = ccxt.mexc({
    'apiKey': os.getenv('API_KEY'),
    'secret': os.getenv('API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

symbol = 'BTC/USDT:USDT'
capital = float(os.getenv('CAPITAL', '400'))

@app.route('/')
def run():
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, '5m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
        df['rsi'] = ta.rsi(df['c'], 14)
        df['vol'] = df['v'] / df['v'].rolling(20).mean()
        rsi = df['rsi'].iloc[-1]
        vol = df['vol'].iloc[-1]
        funding = exchange.fetch_funding_rate(symbol)['fundingRate']
        
        signal = "WAIT"
        if rsi < 30 and vol > 2 and funding < -0.0005: signal = "LONG"
        if rsi > 70 and vol > 2 and funding > 0.0005: signal = "SHORT"
        
        return f"Grok Nano Bot วิ่งอยู่ ✅<br>RSI: {rsi:.1f} | Vol×: {vol:.2f}<br>Funding: {funding:.5f} | Signal: {signal}<br>{time.strftime('%H:%M:%S')}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
