# -*- coding: utf-8 -*-
"""매도 시점용 '연말 종가' 수집 (2016~2025) + 2026 현재가.
   미국주식·코인: yfinance(수정종가) / 한국주식: KRX(pykrx)."""
import json
import pandas as pd
import yfinance as yf
from pykrx import stock

YEARS = list(range(2016, 2026))  # 2016~2025 연말
YF = {"BTC": "BTC-USD", "ETH": "ETH-USD", "DOGE": "DOGE-USD",
      "NVDA": "NVDA", "TSLA": "TSLA", "AAPL": "AAPL"}
KR = {"005930": "삼성전자", "000660": "SK하이닉스", "373220": "LG에너지솔루션"}


def smart_round(v):
    if v is None or pd.isna(v):
        return None
    v = float(v); a = abs(v)
    if a < 0.01: return round(v, 6)
    if a < 1:    return round(v, 4)
    if a < 100:  return round(v, 2)
    if a < 10000:return round(v, 1)
    return int(round(v))


def yearends(close, now_val):
    first = close.index[0]
    row = {}
    for y in YEARS:
        ts = pd.Timestamp(f"{y}-12-31")
        row[f"y{y}"] = None if ts < first else smart_round(close.asof(ts))
    row["now"] = now_val
    return row


results = {}

for key, tk in YF.items():
    df = yf.Ticker(tk).history(period="max", auto_adjust=True)
    df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    c = df["Close"]
    results[key] = yearends(c, smart_round(c.iloc[-1]))
    print(f"[ OK ] {key:6} now {results[key]['now']}")

for code, nm in KR.items():
    df = stock.get_market_ohlcv("20140101", "20260628", code)
    df.index = pd.DatetimeIndex(df.index).normalize()
    c = df["종가"]
    results[code] = yearends(c, int(c.iloc[-1]))
    print(f"[ OK ] {code} {nm} now {results[code]['now']:,}")

with open("sells.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

order = [f"y{y}" for y in YEARS] + ["now"]
print("\n=== JS 주입용 (매도 연말가) key순서: " + ", ".join(order) + " ===")
for key, row in results.items():
    parts = ", ".join(f"{k}:{('null' if row.get(k) is None else row.get(k))}" for k in order)
    print(f'  "{key}": {{ {parts} }},')
