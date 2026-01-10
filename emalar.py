import ccxt
import pandas as pd

# Binance Futures bağlantısı
exchange = ccxt.binance({
    'options': {
        'defaultType': 'future'
    }
})

TIMEFRAME = '1h'      # İstersen 5m, 1h vb. değiştirebilirsin
LIMIT = 100            # EMA hesaplamak için yeterli mum

def get_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def check_ema_crossover(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        df['ema9'] = get_ema(df['close'], 9)
        df['ema21'] = get_ema(df['close'], 21)

        # Son iki mumda yukarı kesişim kontrolü
        prev = df.iloc[-2]
        last = df.iloc[-1]

        if prev['ema9'] < prev['ema21'] and last['ema9'] > last['ema21']:
            return True

    except Exception as e:
        pass

    return False

def scan_futures_markets():
    markets = exchange.load_markets()
    futures_symbols = [
        symbol for symbol in markets
        if symbol.endswith('USDT') and markets[symbol]['future']
    ]

    crossed_symbols = []

    for symbol in futures_symbols:
        if check_ema_crossover(symbol):
            crossed_symbols.append(symbol)

    return crossed_symbols

if __name__ == "__main__":
    results = scan_futures_markets()
    print("EMA 9 / EMA 21 yukarı kesişim olan coinler:")
    for coin in results:
        print(coin)
