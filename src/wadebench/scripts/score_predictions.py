from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wadebench.evaluator.score import score_prediction
from wadebench.io.schema_loader import SchemaLoader


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_tasks(path: Path) -> list[dict]:
    tasks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    return tasks


def find_gold_path(task: dict, gold_root: Path | None) -> Path:
    candidates = []
    if task.get("gold_path"):
        candidates.append(Path(task["gold_path"]))
    if task.get("gold_file"):
        candidates.append(Path(task["gold_file"]))
    src = task.get("source_files", {})
    for k in ["gold", "gold_json", "ground_truth"]:
        if src.get(k):
            candidates.append(Path(src[k]))
    if gold_root:
        task_id = task["task_id"]
        domain = task.get("domain")
        if domain:
            candidates.extend([
                gold_root / domain / f"{task_id}.json",
                gold_root / "by_task" / domain / f"{task_id}.json",
            ])
        candidates.append(gold_root / f"{task_id}.json")
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"Gold file not found for task {task.get('task_id')}. Tried: {[str(c) for c in candidates]}")


def infer_baseline_and_model(pred_dir: Path) -> tuple[str, str]:
    """
    Infer baseline/model names from prediction directory structure.
    Expected: results/predictions/<baseline>/<model>/
    """
    model = pred_dir.name
    baseline = pred_dir.parent.name
    return baseline, model


def make_missing_prediction_row(
    task: dict,
    gold_data: dict,
    pred_path: Path,
    baseline: str,
    model: str,
    record_recall_threshold: float,
    field_f1_threshold: float,
) -> dict:
    """
    Create a failed score row when a prediction file is missing.

    Keeps evaluation denominators fair: every baseline/model has one row per task.
    """
    gold_records = gold_data.get("records", [])
    has_gold = len(gold_records) > 0
    empty_score = 0.0 if has_gold else 1.0

    return {
        "task_id": task.get("task_id", ""),
        "domain": task.get("domain", ""),
        "task_type": task.get("task_type", ""),
        "baseline": baseline,
        "model": model,
        "schema_id": task.get("schema_id", ""),
        # Record-level metrics
        "num_predicted_records": 0,
        "num_gold_records": len(gold_records),
        "record_tp": 0,
        "record_fp": 0,
        "record_fn": len(gold_records),
        "record_precision": empty_score,
        "record_recall": empty_score,
        "record_f1": empty_score,
        # Old matched-record field metrics
        "field_precision": empty_score,
        "field_recall": empty_score,
        "field_f1": empty_score,
        "matched_field_precision": empty_score,
        "matched_field_recall": empty_score,
        "matched_field_f1": empty_score,
        # Field counts
        "field_correct": 0,
        "field_predicted": 0,
        "field_gold": 0,
        "extra_fields": 0,
        # Strict field metrics (Step 5)
        "strict_field_correct": 0,
        "strict_field_predicted": 0,
        "strict_field_gold": 0,
        "strict_field_precision": empty_score,
        "strict_field_recall": empty_score,
        "strict_field_f1": empty_score,
        "strict_micro_field_f1": empty_score,
        # Schema / provenance
        "schema_adherence": 0,
        "provenance_score": 0.0,
        "provenance_field_coverage": 0.0,
        "provenance_quote_coverage": 0.0,
        "selector_coverage": 0.0,
        # Task success
        "task_success": 0,
        "task_success_record_recall_threshold": record_recall_threshold,
        "task_success_field_f1_threshold": field_f1_threshold,
        # Runtime metadata
        "runtime_success": 0,
        "json_valid": 0,
        "latency_seconds": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "repaired": 0,
        # Error metadata
        "error": "missing_prediction",
        "missing_prediction_path": str(pred_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Score prediction JSON files for one baseline/model run.")
    parser.add_argument("--pred-dir", required=True)
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--schemas-dir", default="data/schemas")
    parser.add_argument("--gold-root", default=None)
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--jsonl-output", default=None)
    parser.add_argument("--record-recall-threshold", type=float, default=0.90)
    parser.add_argument("--field-f1-threshold", type=float, default=0.85)
    args = parser.parse_args()

    pred_dir = Path(args.pred_dir)
    tasks = load_tasks(Path(args.tasks))
    schema_loader = SchemaLoader(args.schemas_dir)
    gold_root = Path(args.gold_root) if args.gold_root else None

    rows = []
    missing_count = 0
    baseline_from_dir, model_from_dir = infer_baseline_and_model(pred_dir)

    for task in tasks:
        task_id = task["task_id"]
        pred_path = pred_dir / f"{task_id}.json"

        gold_data = load_json(find_gold_path(task, gold_root))

        if not pred_path.exists():
            print(f"Missing prediction counted as failure: {pred_path}", file=sys.stderr)
            row = make_missing_prediction_row(
                task=task,
                gold_data=gold_data,
                pred_path=pred_path,
                baseline=baseline_from_dir,
                model=model_from_dir,
                record_recall_threshold=args.record_recall_threshold,
                field_f1_threshold=args.field_f1_threshold,
            )
            rows.append(row)
            missing_count += 1
            continue

        prediction = load_json(pred_path)
        schema = schema_loader.load_schema(task.get("schema_id") or prediction.get("schema_id"))
        baseline = prediction.get("baseline") or baseline_from_dir
        row = score_prediction(
            prediction,
            gold_data,
            schema,
            baseline,
            task_success_record_recall=args.record_recall_threshold,
            task_success_field_f1=args.field_f1_threshold,
        )
        # Add task metadata if score_prediction does not already include it.
        row.setdefault("task_type", task.get("task_type", ""))
        row.setdefault("domain", task.get("domain", ""))
        row.setdefault("schema_id", task.get("schema_id", ""))
        row.setdefault("model", prediction.get("model") or model_from_dir)
        rows.append(row)

    out_csv = Path(args.output)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({k for row in rows for k in row.keys()})
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    jsonl_out = Path(args.jsonl_output) if args.jsonl_output else out_csv.with_suffix(".jsonl")
    with jsonl_out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({
        "expected_tasks": len(tasks),
        "scored_rows": len(rows),
        "missing_predictions_counted_as_failures": missing_count,
        "csv": str(out_csv),
        "jsonl": str(jsonl_out),
    }, indent=2))


if __name__ == "__main__":
    main()
