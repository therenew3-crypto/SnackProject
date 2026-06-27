# -*- coding: utf-8 -*-
"""
IF 계좌 계산기 — 실제 역사적 시세 수집 스크립트
yfinance로 각 자산의 (1) 지정 시점 종가, (2) 현재가, (3) 역대 최고가(ATH)를 가져온다.
- 미국주식/코인: auto_adjust=True (액면분할·배당 반영 수정종가)
- 한국주식: .KS 티커
출력: prices.json  +  콘솔에 JS용 ASSET 데이터 + 검수표
"""
import json
import pandas as pd
import yfinance as yf

# 매수 시점 (HTML의 TIMES key와 동일)
DATES = {
    "d20150102": "2015-01-02",
    "d20171217": "2017-12-17",
    "d20181215": "2018-12-15",
    "d20200323": "2020-03-23",
    "d20211109": "2021-11-09",
    "d20220103": "2022-01-03",
    "d20221109": "2022-11-09",
    "d20230102": "2023-01-02",
    "d20240102": "2024-01-02",
    "d20250102": "2025-01-02",
}

# 앱 자산키 -> 야후 티커
TICKERS = {
    "BTC":   "BTC-USD",
    "ETH":   "ETH-USD",
    "DOGE":  "DOGE-USD",
    "NVDA":  "NVDA",
    "TSLA":  "TSLA",
    "AAPL":  "AAPL",
    "005930": "005930.KS",
    "000660": "000660.KS",
    "373220": "373220.KS",
}


def smart_round(v):
    if v is None or pd.isna(v):
        return None
    v = float(v)
    a = abs(v)
    if a < 0.01:
        return round(v, 6)
    if a < 1:
        return round(v, 4)
    if a < 100:
        return round(v, 2)
    if a < 10000:
        return round(v, 1)
    return int(round(v))


def fetch(ticker):
    df = yf.Ticker(ticker).history(period="max", auto_adjust=True)
    if df.empty:
        df = yf.download(ticker, period="max", auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"빈 데이터: {ticker}")
    # tz 제거 + 날짜 정규화
    df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    return df


results = {}
report = []

for key, ticker in TICKERS.items():
    try:
        df = fetch(ticker)
    except Exception as e:
        print(f"[FAIL] {key} ({ticker}): {e}")
        continue

    close = df["Close"]
    high = df["High"]
    first = close.index[0]
    row = {}

    for dk, ds in DATES.items():
        ts = pd.Timestamp(ds)
        if ts < first:
            row[dk] = None  # 상장/데이터 이전
        else:
            val = close.asof(ts)  # 해당일 이전 최근 거래일 종가
            row[dk] = smart_round(val)

    row["now"] = smart_round(close.iloc[-1])
    row["ath"] = smart_round(high.max())

    results[key] = row
    report.append({
        "key": key, "ticker": ticker,
        "data_start": str(first.date()),
        "now": row["now"], "now_date": str(close.index[-1].date()),
        "ath": row["ath"], "ath_date": str(high.idxmax().date()),
    })
    print(f"[ OK ] {key:7} {ticker:10} | start {first.date()} | "
          f"now {row['now']} ({close.index[-1].date()}) | ATH {row['ath']} ({high.idxmax().date()})")

# JSON 저장
with open("prices.json", "w", encoding="utf-8") as f:
    json.dump({"dates": DATES, "assets": results, "report": report}, f, ensure_ascii=False, indent=2)

print("\n=== JS 주입용 가격 (자산키: {시점들}) ===")
order = list(DATES.keys()) + ["now", "ath"]
for key, row in results.items():
    parts = ", ".join(f"{k}:{('null' if row.get(k) is None else row.get(k))}" for k in order)
    print(f'  "{key}": {{ {parts} }},')

print("\nprices.json 저장 완료.")
