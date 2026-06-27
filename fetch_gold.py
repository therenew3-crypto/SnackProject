# -*- coding: utf-8 -*-
"""금(Gold) 시세 수집 — 매수 시점 + 연말 매도 시점. yfinance GC=F (USD/oz)."""
import pandas as pd
import yfinance as yf

DATES = {
    "d20150102": "2015-01-02", "d20171217": "2017-12-17", "d20181215": "2018-12-15",
    "d20200323": "2020-03-23", "d20211109": "2021-11-09", "d20220103": "2022-01-03",
    "d20221109": "2022-11-09", "d20230102": "2023-01-02", "d20240102": "2024-01-02",
    "d20250102": "2025-01-02",
}
YEARS = list(range(2016, 2026))


def sr(v):
    if v is None or pd.isna(v): return None
    return round(float(v), 1)


df = yf.Ticker("GC=F").history(period="max", auto_adjust=True)
df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
c, h = df["Close"], df["High"]
first = c.index[0]
print(f"data start: {first.date()} | now {sr(c.iloc[-1])} ({c.index[-1].date()}) | ATH {sr(h.max())} ({h.idxmax().date()})")

buy = {dk: (None if pd.Timestamp(ds) < first else sr(c.asof(pd.Timestamp(ds)))) for dk, ds in DATES.items()}
buy["now"] = sr(c.iloc[-1]); buy["ath"] = sr(h.max())
sell = {f"y{y}": (None if pd.Timestamp(f"{y}-12-31") < first else sr(c.asof(pd.Timestamp(f"{y}-12-31")))) for y in YEARS}
sell["now"] = sr(c.iloc[-1])

bo = list(DATES.keys()) + ["now", "ath"]
so = [f"y{y}" for y in YEARS] + ["now"]
import json
with open("gold.json", "w", encoding="utf-8") as f:
    json.dump({"assets_order": bo, "sells_order": so, "buy": buy, "sell": sell}, f, ensure_ascii=False, indent=2)
print("ASSETS row:")
print("    " + ", ".join(f"{k}:{('null' if buy[k] is None else buy[k])}" for k in bo))
print("SELLS row:")
print("    " + ", ".join(f"{k}:{('null' if sell[k] is None else sell[k])}" for k in so))
