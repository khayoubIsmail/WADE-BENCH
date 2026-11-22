"""
evaluate_outputs.py — CLI runner for WADE-Bench evaluation.

Usage:
  python scripts/evaluate_outputs.py --baseline B1 --model gpt-4o --split dev
  python scripts/evaluate_outputs.py --baseline B2 --model gemini-2.5-pro --split test
  python scripts/evaluate_outputs.py --baseline B1 --model gpt-4o --split dev --predictions-dir outputs

The script:
  1. Loads tasks from the split file.
  2. Loads predictions from outputs/<baseline>/<model>/<task_id>.json
  3. Loads gold from each task's gold_path.
  4. Runs the evaluator on each (prediction, gold) pair.
  5. Computes macro-averages across the split.
  6. Saves:
     - reports/evaluation/<baseline>/<model>/<split>_metrics.json
     - reports/evaluation/<baseline>/<model>/<split>_per_task.csv
"""

import sys
import os
import json
import csv
import argparse
from pathlib import Path

# Add src directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from wadebench.io.task_loader import TaskLoader
from wadebench.io.schema_loader import SchemaLoader
from wadebench.evaluator.score import score_prediction, load_gold, load_prediction


SPLIT_FILES = {
    "dev": "data/splits/wadebench_v1_3domain_dev.jsonl",
    "test": "data/splits/wadebench_v1_3domain_test.jsonl",
    "all": "data/splits/wadebench_v1_3domain_all.jsonl",
}

METRIC_COLUMNS = [
    "task_id", "domain", "baseline", "model", "schema_id",
    "num_predicted_records", "num_gold_records",
    "record_tp", "record_fp", "record_fn",
    "record_precision", "record_recall", "record_f1",
    "field_precision", "field_recall", "field_f1",
    "schema_adherence", "provenance_score",
    "latency_seconds", "input_tokens", "output_tokens",
    "success", "json_valid", "error",
]


def _safe_mean(values):
    return round(sum(values) / len(values), 4) if values else 0.0


def main():
    parser = argparse.ArgumentParser(description="WADE-Bench Evaluator")
    parser.add_argument("--baseline", required=True, help="Baseline name (e.g. B1, B2, B3, B4)")
    parser.add_argument("--model", required=True, help="Model name (e.g. gpt-4o, gemini-2.5-pro)")
    parser.add_argument("--split", required=True, choices=["dev", "test", "all"], help="Split to evaluate")
    parser.add_argument("--predictions-dir", default="results", help="Root directory for predictions (default: results)")
    args = parser.parse_args()

    split_file = SPLIT_FILES[args.split]
    loader = TaskLoader(split_file)
    schema_loader = SchemaLoader("data/schemas")

    pred_dir = Path(args.predictions_dir) / args.baseline / args.model / args.split

    if not pred_dir.exists():
        print(f"ERROR: Predictions directory not found: {pred_dir}")
        sys.exit(1)

    tasks = loader.load_all_tasks()
    print(f"Evaluating {len(tasks)} tasks for {args.baseline}/{args.model} on {args.split} split")

    all_scores = []
    errors = []

    for task in tasks:
        task_id = task["task_id"]
        schema_id = task["schema_id"]
        gold_path = task["gold_path"]

        # Find prediction file
        pred_path = pred_dir / f"{task_id}.json"
        if not pred_path.exists():
            # Also try <baseline>_<task_id>.json
            pred_path = pred_dir / f"{args.baseline}_{task_id}.json"

        if not pred_path.exists():
            errors.append({"task_id": task_id, "error": f"Prediction file not found: {pred_path}"})
            # Create a zero-score entry for missing predictions
            all_scores.append({
                "task_id": task_id,
                "domain": task.get("domain", ""),
                "baseline": args.baseline,
                "model": args.model,
                "schema_id": schema_id,
                "num_predicted_records": 0,
                "num_gold_records": task.get("num_gold_records", 0),
                "record_tp": 0, "record_fp": 0, "record_fn": task.get("num_gold_records", 0),
                "record_precision": 0.0, "record_recall": 0.0, "record_f1": 0.0,
                "field_precision": 0.0, "field_recall": 0.0, "field_f1": 0.0,
                "schema_adherence": 0, "provenance_score": 0.0,
                "latency_seconds": 0, "input_tokens": 0, "output_tokens": 0,
                "success": False, "json_valid": False, "error": "prediction_missing",
            })
            continue

        try:
            prediction = load_prediction(str(pred_path))
            gold = load_gold(gold_path)
            schema = schema_loader.load_schema(schema_id)

            score = score_prediction(prediction, gold, schema, args.baseline)
            all_scores.append(score)
        except Exception as e:
            errors.append({"task_id": task_id, "error": str(e)})
            all_scores.append({
                "task_id": task_id,
                "domain": task.get("domain", ""),
                "baseline": args.baseline,
                "model": args.model,
                "schema_id": schema_id,
                "num_predicted_records": 0,
                "num_gold_records": task.get("num_gold_records", 0),
                "record_tp": 0, "record_fp": 0, "record_fn": task.get("num_gold_records", 0),
                "record_precision": 0.0, "record_recall": 0.0, "record_f1": 0.0,
                "field_precision": 0.0, "field_recall": 0.0, "field_f1": 0.0,
                "schema_adherence": 0, "provenance_score": 0.0,
                "latency_seconds": 0, "input_tokens": 0, "output_tokens": 0,
                "success": False, "json_valid": False, "error": str(e),
            })

    # --- Compute macro-averages ---
    successful_tasks = [s for s in all_scores if s.get("success")]
    failed_tasks = [s for s in all_scores if not s.get("success")]

    aggregate = {
        "scope": f"WADE-Bench v1 3-domain {args.split}",
        "baseline": args.baseline,
        "model": args.model,
        "split": args.split,
        "total_tasks": len(tasks),
        "evaluated_tasks": len(successful_tasks),
        "failed_tasks": len(failed_tasks),
        "technical_errors": len(errors),
        "failed_task_ids": [s["task_id"] for s in failed_tasks],

        "record_precision": _safe_mean([s["record_precision"] for s in all_scores]),
        "record_recall": _safe_mean([s["record_recall"] for s in all_scores]),
        "record_f1": _safe_mean([s["record_f1"] for s in all_scores]),

        "field_precision": _safe_mean([s["field_precision"] for s in all_scores]),
        "field_recall": _safe_mean([s["field_recall"] for s in all_scores]),
        "field_f1": _safe_mean([s["field_f1"] for s in all_scores]),

        "schema_adherence": _safe_mean([s["schema_adherence"] for s in all_scores]),
        "provenance_score": _safe_mean([s["provenance_score"] for s in all_scores]),

        "latency_seconds": _safe_mean([s["latency_seconds"] for s in all_scores]),
        "input_tokens": sum(s.get("input_tokens", 0) for s in all_scores),
        "output_tokens": sum(s.get("output_tokens", 0) for s in all_scores),

        "errors": errors,
    }

    # --- By-domain breakdown ---
    domains = sorted(set(s["domain"] for s in all_scores))
    by_domain = {}
    for domain in domains:
        domain_scores = [s for s in all_scores if s["domain"] == domain]
        by_domain[domain] = {
            "tasks": len(domain_scores),
            "record_f1": _safe_mean([s["record_f1"] for s in domain_scores]),
            "field_f1": _safe_mean([s["field_f1"] for s in domain_scores]),
            "schema_adherence": _safe_mean([s["schema_adherence"] for s in domain_scores]),
            "provenance_score": _safe_mean([s["provenance_score"] for s in domain_scores]),
        }
    aggregate["by_domain"] = by_domain

    # --- Save outputs ---
    report_dir = Path("reports") / "evaluation" / args.baseline / args.model
    report_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = report_dir / f"{args.split}_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)

    csv_path = report_dir / f"{args.split}_per_task.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=METRIC_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for s in all_scores:
            writer.writerow(s)

    # --- Terminal summary ---
    print(f"\n{'='*60}")
    print(f"  WADE-Bench v1 Evaluation — {args.baseline} / {args.model} / {args.split}")
    print(f"{'='*60}")
    print(f"  Tasks evaluated: {aggregate['total_tasks']}")
    print(f"  Successful:      {aggregate['evaluated_tasks']}")
    print(f"  Failed:          {aggregate['failed_tasks']}")
    print(f"{'-'*60}")
    print(f"  Record Precision: {aggregate['record_precision']:.4f}")
    print(f"  Record Recall:    {aggregate['record_recall']:.4f}")
    print(f"  Record F1:        {aggregate['record_f1']:.4f}")
    print(f"{'-'*60}")
    print(f"  Field Precision:  {aggregate['field_precision']:.4f}")
    print(f"  Field Recall:     {aggregate['field_recall']:.4f}")
    print(f"  Field F1:         {aggregate['field_f1']:.4f}")
    print(f"{'-'*60}")
    print(f"  Schema Adherence: {aggregate['schema_adherence']:.4f}")
    print(f"  Provenance Score: {aggregate['provenance_score']:.4f}")
    print(f"{'-'*60}")
    print(f"  Avg Latency (s):  {aggregate['latency_seconds']:.2f}")
    print(f"  Total In Tokens:  {aggregate['input_tokens']}")
    print(f"  Total Out Tokens: {aggregate['output_tokens']}")
    print(f"{'='*60}")
    print(f"\n  Per-domain breakdown:")
    for domain, dm in by_domain.items():
        print(f"    {domain}: {dm['tasks']} tasks | record_f1={dm['record_f1']:.4f} | field_f1={dm['field_f1']:.4f}")

    print(f"\n  Reports saved to:")
    print(f"    {metrics_path}")
    print(f"    {csv_path}")


if __name__ == "__main__":
    main()
