# Linkareer 자소서 수집기

링커리어(linkareer.com)의 합격 자기소개서를 키워드로 검색해 수집하고, 엑셀 파일로 변환하는 Selenium 기반 스크레이퍼입니다.

## 환경 설정

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 실행 방법

```bash
# 1단계: 자소서 수집 → JSONL 파일 생성
python main.py "백엔드 개발자"

# 출력 파일명을 직접 지정하고 싶을 때
python main.py "백엔드 개발자" -o my_output.jsonl

# 2단계: JSONL → 엑셀 변환
python jsonl_to_exel.py
```

## 파일 구조

```
linkareer_data/
├── main.py                          # 메인 스크레이퍼
├── jsonl_to_exel.py                 # JSONL → 엑셀 변환기
├── linkareer_backend_developer.jsonl  # 수집 결과 (gitignore됨)
└── linkareer_backend_developer.xlsx   # 변환된 엑셀 파일
```

## 동작 방식

### 1단계: 링크 수집 (`get_all_links`)

`linkareer.com/cover-letter/search?role=<검색어>` 페이지를 순회하며 자소서 URL을 모두 수집합니다. 페이지에 결과가 없어질 때까지 자동으로 다음 페이지로 넘어갑니다.

### 2단계: 상세 파싱 (`parse_cover_letter`)

각 자소서 URL에 접근해 아래 정보를 추출합니다.

| 필드 | 설명 |
|---|---|
| `company` | 기업명 |
| `job` | 직무 |
| `season` | 채용 시즌 (예: 2025 하반기) |
| `spec` | 합격자 스펙 |
| `questions` | 문항/답변 리스트 |

#### 본문 파싱 파이프라인

페이지 body에서 사이드바 노이즈를 제거하고 실제 자소서 본문만 추출합니다.

1. **Copyright 경계** — `Copyright © Linkareer Inc. All Rights Reserved.` 이후 내용만 사용
2. **번호 항목 분리** — `1. 문항` 형태로 된 항목을 개별 Q&A로 분리
3. **자유양식 처리** — 번호 없는 자유형 자소서는 `[자유양식]`으로 단일 항목 처리
4. **후처리** — `\n새창\n목록` 등 UI 노이즈 제거

### JSONL → 엑셀 변환

`jsonl_to_exel.py`는 JSONL의 각 자소서를 문항 단위로 펼쳐서(flatten) 엑셀로 저장합니다. 자소서 1건에 문항이 여러 개면 여러 행으로 나뉩니다.

**엑셀 컬럼:** `url`, `keyword`, `company`, `job`, `season`, `spec`, `question`, `answer`

## 옵션

| 인자 | 설명 |
|---|---|
| `keyword` (필수) | 검색할 직무 키워드 |
| `-o`, `--output` | 출력 JSONL 파일 경로 (생략 시 `키워드.jsonl` 자동 생성) |

```bash
# 도움말 확인
python main.py --help
```

## 주의 사항

- 로그인 없이 접근 가능한 공개 자소서만 수집합니다.
- Chrome 브라우저가 설치되어 있어야 합니다 (ChromeDriver는 자동 설치).
- 기본값은 헤드리스 모드 OFF입니다. 헤드리스로 실행하려면 `get_driver(headless=True)`로 변경하세요.
- 요청 간 2.5초 딜레이가 적용됩니다.
