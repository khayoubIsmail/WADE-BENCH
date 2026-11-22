import json
from pathlib import Path
import csv

BASELINES = [
    "b1_html_llm",
    "b2_markdown_llm",
    "b3_vision_llm",
    "b4_playwright_mcp_agent",
]

MODEL = "ollama_gemma4_131k"
SPLIT = "test"

rows = []

for baseline in BASELINES:
    path = Path("reports") / "evaluation" / baseline / MODEL / f"{SPLIT}_metrics.json"

    if not path.exists():
        print(f"Missing: {path}")
        continue

    data = json.loads(path.read_text(encoding="utf-8"))

    rows.append({
        "baseline": baseline,
        "model": MODEL,
        "split": SPLIT,
        "record_precision": data.get("record_precision"),
        "record_recall": data.get("record_recall"),
        "record_f1": data.get("record_f1"),
        "field_precision": data.get("field_precision"),
        "field_recall": data.get("field_recall"),
        "field_f1": data.get("field_f1"),
        "schema_adherence": data.get("schema_adherence"),
        "provenance_score": data.get("provenance_score"),
        "latency_seconds": data.get("latency_seconds"),
        "failed_tasks": data.get("failed_tasks"),
        "evaluated_tasks": data.get("evaluated_tasks"),
    })

out_dir = Path("reports") / "comparison"
out_dir.mkdir(parents=True, exist_ok=True)

out_csv = out_dir / f"{MODEL}_{SPLIT}_baseline_comparison.csv"

with out_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved: {out_csv}")
for r in rows:
    print(r)
