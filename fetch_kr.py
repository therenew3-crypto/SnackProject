# -*- coding: utf-8 -*-
"""한국 종목(삼성전자/SK하이닉스/LG엔솔)을 KRX 공식 데이터(pykrx)로 수집."""
import json
import pandas as pd
from pykrx import stock

DATES = {
    "d20150102": "2015-01-02", "d20171217": "2017-12-17", "d20181215": "2018-12-15",
    "d20200323": "2020-03-23", "d20211109": "2021-11-09", "d20220103": "2022-01-03",
    "d20221109": "2022-11-09", "d20230102": "2023-01-02", "d20240102": "2024-01-02",
    "d20250102": "2025-01-02",
}
KR = {"005930": "삼성전자", "000660": "SK하이닉스", "373220": "LG에너지솔루션"}

START, END = "20140101", "20260628"
results = {}

for code, nm in KR.items():
    df = stock.get_market_ohlcv(START, END, code)  # 시가 고가 저가 종가 거래량
    df.index = pd.DatetimeIndex(df.index).normalize()
    close, high = df["종가"], df["고가"]
    first = close.index[0]
    row = {}
    for dk, ds in DATES.items():
        ts = pd.Timestamp(ds)
        row[dk] = None if ts < first else int(close.asof(ts))
    row["now"] = int(close.iloc[-1])
    row["ath"] = int(high.max())
    results[code] = row
    print(f"[ OK ] {code} {nm:8} | start {first.date()} | now {row['now']:,} "
          f"({close.index[-1].date()}) | ATH {row['ath']:,} ({high.idxmax().date()})")

with open("prices_kr.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

order = list(DATES.keys()) + ["now", "ath"]
print("\n=== JS 주입용 (한국) ===")
for code, row in results.items():
    parts = ", ".join(f"{k}:{('null' if row.get(k) is None else row.get(k))}" for k in order)
    print(f'  "{code}": {{ {parts} }},')
