import json
import pandas as pd

INPUT_FILE  = "linkareer_backend_developer.jsonl"
OUTPUT_FILE = "linkareer_backend_developer.xlsx"

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