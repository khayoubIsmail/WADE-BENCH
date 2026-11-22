from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wadebench.evaluator.error_taxonomy import taxonomy_rows, add_error_labels

NUMERIC_MEAN_FIELDS = [
    "record_precision", "record_recall", "record_f1",

    # Old matched-record macro field metric
    "field_precision", "field_recall", "field_f1",
    "matched_field_precision", "matched_field_recall", "matched_field_f1",

    # New strict whole-task field metric (use this for the paper)
    "strict_field_precision", "strict_field_recall", "strict_field_f1",
    "strict_micro_field_f1",

    "schema_adherence", "provenance_score", "provenance_field_coverage",
    "provenance_quote_coverage", "selector_coverage",
    "task_success", "runtime_success", "json_valid", "latency_seconds",
]
NUMERIC_SUM_FIELDS = [
    "num_predicted_records", "num_gold_records",
    "record_tp", "record_fp", "record_fn",

    # Old matched-record field counts
    "field_correct", "field_predicted", "field_gold", "extra_fields",

    # New strict field counts
    "strict_field_correct", "strict_field_predicted", "strict_field_gold",

    "input_tokens", "output_tokens", "total_tokens",
]


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(v):
    if isinstance(v, bool):
        return 1.0 if v else 0.0

    if isinstance(v, str):
        if v.lower() == "true":
            return 1.0
        if v.lower() == "false":
            return 0.0

    try:
        if v in (None, "", "None"):
            return 0.0
        return float(v)
    except Exception:
        return 0.0


def aggregate(rows: list[dict], group_fields: list[str]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        key = tuple(row.get(g, "") for g in group_fields)
        groups[key].append(row)

    out = []
    for key, vals in groups.items():
        item = {g: key[i] for i, g in enumerate(group_fields)}
        item["num_tasks"] = len(vals)
        for f in NUMERIC_MEAN_FIELDS:
            item[f"mean_{f}"] = round(sum(to_float(v.get(f)) for v in vals) / len(vals), 4) if vals else 0.0
        for f in NUMERIC_SUM_FIELDS:
            item[f"sum_{f}"] = round(sum(to_float(v.get(f)) for v in vals), 4)
        out.append(item)
    return sorted(out, key=lambda x: tuple(str(x.get(g, "")) for g in group_fields))


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Aggregate WADE-Bench score CSV files.")
    parser.add_argument("--scores", nargs="+", required=True, help="One or more per-task score CSV files")
    parser.add_argument("--output-dir", default="results/aggregate")
    args = parser.parse_args()

    rows = []
    for p in args.scores:
        rows.extend(read_csv(Path(p)))

    out_dir = Path(args.output_dir)
    # Per-task scores with error labels
    labeled_rows = add_error_labels(rows)

    write_csv(out_dir / "all_per_task_scores.csv", labeled_rows)

    # Main aggregate tables
    write_csv(out_dir / "aggregate_by_baseline_model.csv", aggregate(rows, ["baseline", "model"]))
    write_csv(out_dir / "aggregate_by_domain_baseline_model.csv", aggregate(rows, ["domain", "baseline", "model"]))
    write_csv(out_dir / "aggregate_by_domain.csv", aggregate(rows, ["domain"]))
    write_csv(out_dir / "aggregate_by_baseline.csv", aggregate(rows, ["baseline"]))
    write_csv(out_dir / "aggregate_by_model.csv", aggregate(rows, ["model"]))

    write_csv(out_dir / "aggregate_by_task_type.csv", aggregate(rows, ["task_type"]))
    write_csv(out_dir / "aggregate_by_domain_task_type.csv", aggregate(rows, ["domain", "task_type"]))
    write_csv(
        out_dir / "aggregate_by_baseline_model_task_type.csv",
        aggregate(rows, ["baseline", "model", "task_type"]),
    )

    # Failure-taxonomy tables
    write_csv(out_dir / "failure_taxonomy.csv", taxonomy_rows(rows))
    write_csv(out_dir / "failure_taxonomy_by_baseline_model.csv", taxonomy_rows(rows, ["baseline", "model"]))
    write_csv(out_dir / "failure_taxonomy_by_domain.csv", taxonomy_rows(rows, ["domain"]))
    write_csv(
        out_dir / "failure_taxonomy_by_domain_baseline_model.csv",
        taxonomy_rows(rows, ["domain", "baseline", "model"]),
    )

    print(json.dumps({"input_score_files": len(args.scores), "input_rows": len(rows), "output_dir": str(out_dir)}, indent=2))


if __name__ == "__main__":
    main()
