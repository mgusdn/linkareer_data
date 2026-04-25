import json
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="JSONL → 엑셀 변환기")
parser.add_argument("input", help="입력 JSONL 파일 경로")
parser.add_argument("-o", "--output", help="출력 엑셀 파일 경로 (기본값: 입력 파일명.xlsx)")
args = parser.parse_args()

INPUT_FILE  = args.input
OUTPUT_FILE = args.output if args.output else args.input.rsplit(".", 1)[0] + ".xlsx"

# ── JSONL 로드 (줄별로 읽기) ───────────────────────
data = []
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            data.append(json.loads(line))

# ── 데이터 펼치기 ──────────────────────────────────
rows = []
for item in data:
    base = {
        "url":     item.get("url", ""),
        "keyword": item.get("keyword", ""),
        "company": item.get("company", ""),
        "job":     item.get("job", ""),
        "season":  item.get("season", ""),
        "spec":    item.get("spec", ""),
    }
    questions = item.get("questions", [])
    if questions:
        for q in questions:
            rows.append({
                **base,
                "question": q.get("question", ""),
                "answer":   q.get("answer", ""),
            })
    else:
        rows.append({**base, "question": "", "answer": ""})

# ── 엑셀 저장 ──────────────────────────────────────
df = pd.DataFrame(rows)
df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ 완료! 총 {len(df)}행 → {OUTPUT_FILE}")
