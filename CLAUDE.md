# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트
기업명을 입력하면 최근 5개년 재무를 분석해 위험등급(좋음/주의/나쁨)을 보여주는 브라우저 기반 웹앱. 빌드·린트·테스트 도구는 없다.

## 명령
- 실행: `index.html`을 브라우저로 열기
- Playwright MCP는 `file://`을 막으므로 로컬 서버 필요: `python3 -m http.server 8765` → `http://localhost:8765/index.html` (서버 기동이 권한 검사에서 거부될 수 있어 사용자가 `!`로 직접 실행해야 할 수 있음)
- 브라우저 없이 로직만 검증: `index.html`의 `<script>`를 추출해 Node `vm`에서 DOM/`localStorage` 스텁과 함께 실행
- 수정 후 확인: 삼성전자 → 좋음 10/10, 새로고침 후 결과·조회 기록 유지, 없는 기업 안내, 콘솔 에러 0건, 375px 가로 스크롤 없음

## 아키텍처
앱 전체가 `index.html` 한 파일(CSS + JS 인라인, 외부 의존성 없음, 50KB 이하 유지)이다. 흐름은 `run(q)` → 기업명 정규화(소문자·공백 제거 후 `DATA` 키/`ALIAS` 비교) → `analyze()`(5개 지표를 `pick()`으로 0~2점 환산, 합계로 등급) → `localStorage`(`corp-risk-v1`)에 `{q, result, hist}` 저장 → `render()`/`renderHist()`. 초기 로드 시 저장된 `result`를 그대로 렌더하므로 `analyze()` 반환 구조(`name, score, level, items, d`)를 바꾸면 이전에 저장된 데이터와 호환되지 않는다.

- 등급 기준(7~10 좋음 / 4~6 주의 / 0~3 나쁨)과 지표별 임계값은 `PRD.md` 5장과 `analyze()`/`pick()` 두 곳에 있으며 항상 일치해야 한다
- 등급 이름은 PRD 최초 요청(주의/보통/나쁨)과 달리 `LEVELS` 상수의 좋음/주의/나쁨. CSS 클래스명도 등급 한글 이름(`.좋음` 등)을 그대로 쓰므로 이름을 바꾸면 CSS도 함께 바꿔야 함
- `DATA`는 내장 샘플(단위 조원, 2020~2024, 4개 기업). 기억 기반 근사치이며 DART와 대조하지 않았다. 새 기업 추가 시 `years/rev/op/ni/assets/liab/equity/ca/cl` 배열을 모두 채울 것
- 사용자 입력이 들어가는 `innerHTML`은 `esc()`로 이스케이프(오류 메시지, 칩)

## 저장소 구성
- `PRD.md`: 요구사항과 수용 기준. `PROMPTS.md`: 1~4단계 개발 프롬프트
- `*.ipynb`(`데이터수집_Dart.ipynb`, `기업예측.ipynb`, `Untitled.ipynb`): 웹앱과 별개의 DART 수집·모델링 실험 노트북. 앱에서 참조하지 않으며, 깃에 올리지 않기로 했음(`.gitignore`로 제외). 비밀값 포함 여부는 확인하지 않았음
- GitHub 업로드는 진행 중: `git init`과 스테이징만 완료, 커밋·push는 미실행(커밋용 이름과 원격 저장소 URL 필요, `gh` 미설치)

## 작업 규칙
- 커밋·push 등 외부에 영향을 주는 작업은 먼저 확인받기
- 한국어로 답변
