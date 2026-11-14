"""CSV(kospi_top200_financial_ml_2020_2024.csv) -> index.html 내장 DATA 갱신.

사용: python3 build_data.py
index.html 안의 `/*DATA*/ ... /*END*/` 구간만 교체한다.
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
CSV = ROOT / "kospi_top200_financial_ml_2020_2024.csv"
HTML = ROOT / "index.html"

COLS = {  # 짧은 키: CSV 컬럼 (단위 억원)
    "r": "revenue_eok",
    "o": "operating_profit_eok",
    "n": "net_income_eok",
    "a": "total_assets_eok",
    "l": "total_liabilities_eok",
    "e": "total_equity_eok",
    "ca": "current_assets_eok",
    "cl": "current_liabilities_eok",
}

df = pd.read_csv(CSV, dtype={"corp_code": str, "stock_code": str})
data = {}
for name, g in df.sort_values("year").groupby("corp_name"):
    item = {"c": g["stock_code"].iloc[0], "y": [int(y) for y in g["year"]]}
    if (g["selected_fs"] == "OFS").any():
        item["ofs"] = 1  # 별도재무제표 사용
    for k, col in COLS.items():
        item[k] = [None if pd.isna(v) else round(float(v)) for v in g[col]]
    data[name] = item

blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = HTML.read_text(encoding="utf-8")
new, n = re.subn(r"/\*DATA\*/.*?/\*END\*/", lambda _: f"/*DATA*/{blob}/*END*/", html, flags=re.S)
assert n == 1, "index.html에서 /*DATA*/ ... /*END*/ 구간을 찾지 못함"
HTML.write_text(new, encoding="utf-8")
print(f"{len(data)}개 기업, DATA {len(blob) / 1024:.0f}KB 반영")
