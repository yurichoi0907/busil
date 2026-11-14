# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트
기업명을 입력하면 최근 5개년 재무를 분석해 위험등급(좋음/주의/나쁨)을 보여주는 브라우저 기반 웹앱. 빌드·린트·테스트 도구는 없다.

## 명령
- 실행: `index.html`을 브라우저로 열기
- Playwright MCP는 `file://`을 막으므로 로컬 서버 필요: `python3 -m http.server 8765` → `http://localhost:8765/index.html` (서버 기동이 권한 검사에서 거부될 수 있어 사용자가 `!`로 직접 실행해야 할 수 있음)
- 브라우저 없이 로직만 검증: `index.html`의 `<script>`를 추출해 Node `vm`에서 DOM/`localStorage` 스텁과 함께 실행
- 수정 후 확인: 삼성전자 → 좋음, 새로고침 후 결과·조회 기록 유지, 없는 기업 안내, 콘솔 에러 0건, 375px 가로 스크롤 없음

## 아키텍처
앱 전체가 `index.html` 한 파일(CSS + JS 인라인, 외부 의존성 없음)이다. `DATA`는 `/*DATA*/...{}.../*END*/` 구간에 들어 있고, **직접 수정하지 말고** `python3 -I build_data.py`로 `kospi_top200_financial_ml_2020_2024.csv`에서 재생성한다(pandas 필요). 흐름은 `run(q)` → `find()`(별칭 → 정확/종목코드 → 접두 → 포함 순 매칭, 여러 개면 후보 칩 표시) → `analyze()`(최근 연도 지표 계산 후 `gradeOf()`로 등급) → `summarize()`(규칙 기반 요약) → `localStorage`(`corp-risk-v2`)에 `{q, result, hist}` 저장 → `render()`. 초기 로드 시 저장된 `result`를 그대로 렌더하므로 `analyze()` 반환 구조를 바꾸면 `KEY` 버전을 올려야 한다.

- 등급 규칙(`gradeOf`)은 `기업예측.ipynb` STEP 3의 라벨 규칙과 `PRD.md` 5장과 항상 일치해야 한다. 변경 후에는 CSV 라벨과 196개사 전부 대조할 것(현재 0건 불일치)
- 지표가 하나라도 결측이면 등급을 "보류"로 처리(금융업 25개사). 판정·요약은 모두 브라우저 안에서 규칙으로 생성하며 LLM API 키는 쓰지 않는다
- 등급 이름은 PRD 최초 요청(주의/보통/나쁨)과 달리 좋음/주의/나쁨. CSS 클래스명이 등급 한글 이름(`.좋음`, `.보류` 등)을 그대로 쓰므로 이름을 바꾸면 CSS도 함께 바꿔야 함
- 사용자 입력이 들어가는 `innerHTML`은 `esc()`로 이스케이프

## 저장소 구성
- `build_data.py`: CSV → `index.html` DATA 변환
- `PRD.md`: 요구사항과 수용 기준. `PROMPTS.md`: 1~4단계 개발 프롬프트
- `기업예측.ipynb`(KOSPI 200 CSV로 다음 연도 등급을 랜덤포레스트로 예측하는 팀 실험), `데이터수집_Dart.ipynb`, `Untitled.ipynb`: 웹앱과 별개이며 앱이 참조하지 않음. 깃에 올리지 않음(`.gitignore`). `데이터수집_Dart.ipynb`의 비밀값 포함 여부는 확인하지 않았음
- GitHub 업로드는 사용자가 직접 진행하기로 함

## 작업 규칙
- 커밋·push 등 외부에 영향을 주는 작업은 먼저 확인받기
- 한국어로 답변
