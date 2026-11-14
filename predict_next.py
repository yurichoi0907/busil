"""다음 해 위험등급 예측 -> index.html 내장 PRED 갱신.

기업예측.ipynb 와 같은 라벨 규칙/특성/랜덤포레스트 설정을 사용한다.
- 검증: 2020~2022 -> 2023 의 다음 해 등급으로 학습, 2023 -> 2024 예측 정확도 출력 (노트북과 동일)
- 서비스용: 가능한 모든 연도쌍(2020~2023 -> 다음 해)으로 다시 학습해 2024 지표로 2025 등급 예측
사용: python3 -I predict_next.py   (pandas, scikit-learn 필요)
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).parent
CSV = ROOT / "kospi_top200_financial_ml_2020_2024.csv"
HTML = ROOT / "index.html"
FEATURES = ["debt_ratio", "current_ratio", "operating_margin", "roe", "roa", "revenue_growth"]
REQUIRED = ["operating_margin", "current_ratio", "debt_ratio"]

df = pd.read_csv(CSV, dtype={"corp_code": str, "stock_code": str})

# 라벨 (좋음=0, 주의=1, 나쁨=2, 판정 불가=NaN) -- 노트북 STEP 3, index.html gradeOf 와 동일
bad = (df["operating_margin"] < 0) | ((df["current_ratio"] < 100) & (df["debt_ratio"] > 200))
good = (df["current_ratio"] >= 150) & (df["operating_margin"] >= 5) & (df["debt_ratio"] <= 100)
df["label"] = np.select([bad, good], [2, 0], default=1).astype(float)
df.loc[df[REQUIRED].isna().any(axis=1), "label"] = np.nan

# 다음 해 라벨 연결 (노트북 STEP 5)
df = df.sort_values(["corp_code", "year"])
df["next_label"] = df.groupby("corp_code")["label"].shift(-1)
df["next_year"] = df.groupby("corp_code")["year"].shift(-1)
pairs = df[(df["next_year"] == df["year"] + 1) & df["next_label"].notna()].copy()
pairs["next_label"] = pairs["next_label"].astype(int)


def fit(train):
    imp = SimpleImputer(strategy="median")
    X = imp.fit_transform(train[FEATURES])
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, train["next_label"])
    return imp, model


# 1) 노트북과 같은 홀드아웃 검증
tr, te = pairs[pairs["year"] <= 2022], pairs[pairs["year"] == 2023]
imp, model = fit(tr)
acc = accuracy_score(te["next_label"], model.predict(imp.transform(te[FEATURES])))
print(f"홀드아웃(2023->2024) 정확도 {acc * 100:.2f}%  (학습 {len(tr)}, 테스트 {len(te)})")

# 2) 서비스용: 전체 연도쌍으로 학습 -> 2024 지표로 2025 예측
imp, model = fit(pairs)
cur = df[(df["year"] == 2024) & df["label"].notna()].copy()  # 2024 등급 판정 가능한 기업만
proba = model.predict_proba(imp.transform(cur[FEATURES]))
cls = list(model.classes_)
out = {}
for (_, row), p in zip(cur.iterrows(), proba):
    pct = [round(float(p[cls.index(c)]) * 100) if c in cls else 0 for c in (0, 1, 2)]
    out[row["corp_name"]] = pct  # [좋음%, 주의%, 나쁨%]

meta = {"acc": round(acc * 100), "n": len(pairs), "year": 2025}
blob = json.dumps({"meta": meta, "p": out}, ensure_ascii=False, separators=(",", ":"))
html = HTML.read_text(encoding="utf-8")
new, n = re.subn(r"/\*PRED\*/.*?/\*PEND\*/", lambda _: f"/*PRED*/{blob}/*PEND*/", html, flags=re.S)
assert n == 1, "index.html에서 /*PRED*/ ... /*PEND*/ 구간을 찾지 못함"
HTML.write_text(new, encoding="utf-8")
print(f"{len(out)}개 기업 2025 예측 반영 ({len(blob) / 1024:.1f}KB)")
