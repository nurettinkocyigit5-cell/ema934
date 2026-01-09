import streamlit as st
import ccxt
import pandas as pd

st.set_page_config(
    page_title="Gate.io EMA9 / EMA34 Scanner",
    layout="wide"
)

st.title("📈 Gate.io EMA9 → EMA34 Yukarı Kesişim Tarayıcı")
st.caption("TradingView EMA hesaplaması ile birebir uyumlu | 1 Saatlik")

TIMEFRAME = "1h"
LIMIT = 120

@st.cache_data(ttl=300)
def get_symbols():
    exchange = ccxt.gateio({
        'enableRateLimit': True
    })
    markets = exchange.load_markets()

    return [
        s for s in markets
        if s.endswith('/USDT')
        and markets[s]['active']
        and markets[s]['spot']
    ]

def ema(series, period):
    # TradingView EMA ile birebir
    return series.ewm(span=period, adjust=False).mean()

def scan():
    exchange = ccxt.gateio({
        'enableRateLimit': True
    })

    rows = []

    for symbol in get_symbols():
        try:
            ohlcv = exchange.fetch_ohlcv(
                symbol,
                timeframe=TIMEFRAME,
                limit=LIMIT
            )

            df = pd.DataFrame(
                ohlcv,
                columns=['time', 'open', 'high', 'low', 'close', 'volume']
            )

            df['ema9'] = ema(df['close'], 9)
            df['ema34'] = ema(df['close'], 34)

            prev_ema9 = df['ema9'].iloc[-2]
            prev_ema34 = df['ema34'].iloc[-2]

            curr_ema9 = df['ema9'].iloc[-1]
            curr_ema34 = df['ema34'].iloc[-1]

            # EMA9 aşağıdan yukarı EMA34 kesişimi
            if prev_ema9 < prev_ema34 and curr_ema9 > curr_ema34:
                rows.append({
                    "Coin": symbol,
                    "EMA9": round(curr_ema9, 4),
                    "EMA34": round(curr_ema34, 4),
                    "Fark %": round(
                        (curr_ema9 - curr_ema34) / curr_ema34 * 100, 2
                    )
                })

        except:
            continue

    return pd.DataFrame(rows)

# 🔘 TARAMAYI BAŞLAT BUTONU
if st.button("🚀 Taramayı Başlat"):
    with st.spinner("Gate.io taranıyor..."):
        result = scan()

    if result.empty:
        st.warning("Kesişim bulunamadı.")
    else:
        st.success(f"{len(result)} coin bulundu")
        st.dataframe(
            result.sort_values("Fark %", ascending=False),
            use_container_width=True
        )

st.markdown("---")
st.caption("⚠️ TradingView EMA ile birebir uyumludur. Yatırım tavsiyesi değildir.")
