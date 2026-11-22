from __future__ import annotations

import csv
from pathlib import Path


AGG = Path("results/aggregate")
PAPER = Path("results/paper_tables")
PAPER.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def round_float(x, ndigits=4):
    try:
        return round(float(x), ndigits)
    except Exception:
        return x


def compact(rows: list[dict], fields: list[str]) -> list[dict]:
    out = []
    for row in rows:
        item = {}
        for f in fields:
            value = row.get(f, "")
            if f.startswith("mean_") or f.startswith("sum_"):
                value = round_float(value)
            item[f] = value
        out.append(item)
    return out


# Table 1: Main baseline/model results
main_fields = [
    "baseline",
    "model",
    "n",
    "mean_record_f1",
    "mean_strict_field_f1",
    "mean_schema_adherence",
    "mean_provenance_score",
    "mean_task_success",
    "sum_input_tokens",
    "sum_output_tokens",
    "sum_total_tokens",
    "mean_latency_seconds",
]

rows = read_csv(AGG / "aggregate_by_baseline_model.csv")
write_csv(
    PAPER / "table_main_results.csv",
    compact(rows, main_fields),
    main_fields,
)


# Table 2: Domain breakdown
domain_fields = [
    "domain",
    "baseline",
    "model",
    "n",
    "mean_record_f1",
    "mean_strict_field_f1",
    "mean_task_success",
]

rows = read_csv(AGG / "aggregate_by_domain_baseline_model.csv")
write_csv(
    PAPER / "table_domain_breakdown.csv",
    compact(rows, domain_fields),
    domain_fields,
)


# Table 3: Listing vs detail
task_type_path = AGG / "aggregate_by_task_type.csv"
if task_type_path.exists():
    task_type_fields = [
        "task_type",
        "n",
        "mean_record_f1",
        "mean_strict_field_f1",
        "mean_schema_adherence",
        "mean_provenance_score",
        "mean_task_success",
    ]

    rows = read_csv(task_type_path)
    write_csv(
        PAPER / "table_listing_vs_detail.csv",
        compact(rows, task_type_fields),
        task_type_fields,
    )


# Table 4: Failure taxonomy
failure_fields = [
    "error_type",
    "count",
    "rate",
    "num_tasks",
]

rows = read_csv(AGG / "failure_taxonomy.csv")
write_csv(
    PAPER / "table_failure_taxonomy.csv",
    rows,
    failure_fields,
)


# Table 5: Failure taxonomy by baseline/model
failure_bm_fields = [
    "baseline",
    "model",
    "error_type",
    "count",
    "rate",
    "num_tasks",
]

rows = read_csv(AGG / "failure_taxonomy_by_baseline_model.csv")
write_csv(
    PAPER / "table_failure_taxonomy_by_baseline_model.csv",
    rows,
    failure_bm_fields,
)

print(f"Wrote paper tables to {PAPER}")
