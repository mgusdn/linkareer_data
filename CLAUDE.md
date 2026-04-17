# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install selenium webdriver-manager pandas openpyxl
```

## Running

```bash
# Main scraper — collects cover letters and writes to JSONL
python main.py

# Convert JSONL to Excel
python jsonl_to_exel.py

# Selector inspector — debug helper, dumps all <input> and "직무" elements
python find_selector.py
```

## Architecture

Selenium scraper targeting `linkareer.com/cover-letter/search`, two-phase:

1. **Link collection** (`get_all_links`) — paginates the search results page and collects `/cover-letter/<id>` URLs via JS querySelector on `[class*="coverletter-content"]`
2. **Detail parsing** (`parse_cover_letter`) — visits each URL, extracts metadata from `<h1>` / `<h3>`, then parses Q&A from `body.text`

### Body text parsing pipeline

The page body contains sidebar noise (recommended covers, footer) before the actual cover letter. Parsing strips it in layers:

1. **Copyright boundary** — everything before `Copyright © Linkareer Inc. All Rights Reserved.\n` is discarded
2. **Numbered split** — `re.split(r'\n(?=\d+\.\s)', content)` splits into sections; sections matching `^\d+\.` become individual `{question, answer}` entries
3. **Free-form fallback** — if no numbered sections found, uses `다시보지 않기\n` as secondary boundary, then strips `자세히 알아보기` ad blocks and `[자유양식]`/`자유 항목` labels
4. **Trailing noise** — `\n새창\n목록` removed from all answers

Output is newline-delimited JSON, one record per cover letter.

## Key constants (main.py)

| Variable | Default | Purpose |
|---|---|---|
| `KEYWORD` | `"백엔드 개발자"` | Search term passed as `role=` query param |
| `OUTPUT` | `"linkareer_backend_developer.jsonl"` | Output file path |
