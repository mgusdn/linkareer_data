# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install selenium webdriver-manager
```

## Running

```bash
# Main scraper — collects cover letters and writes to cover_letters.jsonl
python main.py

# Selector inspector — opens browser and prints all input/job-related elements for debugging
python find_selector.py
```

## Architecture

Two-script Selenium scraper targeting `linkareer.com/cover-letter/search`.

**`main.py`** — production scraper, two-phase:
1. Crawls search result pages to collect `/cover-letter/<id>` links (`get_all_links`)
2. Visits each link and parses company, job, season, spec, and Q&A sections (`parse_cover_letter`)
   - Output: newline-delimited JSON (`cover_letters.jsonl`), one record per cover letter
   - Parsing relies on `body.text` pattern matching (`문장 스크랩` boundary + numbered sections), not DOM selectors — fragile to page layout changes

**`find_selector.py`** — one-off debug utility; opens the search page and dumps all `<input>` elements and nodes containing "직무" to stdout. Run this when CSS selectors in `main.py` stop working.

## Key constants (main.py)

| Variable | Default | Purpose |
|---|---|---|
| `KEYWORD` | `"백엔드 개발자"` | Search term passed as `role=` query param |
| `OUTPUT` | `"cover_letters.jsonl"` | Output file path (relative to cwd) |
