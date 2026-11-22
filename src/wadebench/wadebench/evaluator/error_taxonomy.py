from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    """Convert CSV/string/boolean values into float safely."""
    if value is None:
        return default
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if value == "" or value.lower() in {"none", "null", "nan"}:
            return default
        if value.lower() == "true":
            return 1.0
        if value.lower() == "false":
            return 0.0
    try:
        return float(value)
    except Exception:
        return default


def _to_bool(value: Any) -> bool:
    """Convert CSV/string/boolean values into bool safely."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        value = value.strip().lower()
        if value in {"true", "1", "yes", "y"}:
            return True
        if value in {"false", "0", "no", "n", "", "none", "null"}:
            return False
    return False


def _error_text(row: dict) -> str:
    """Normalize the error field."""
    err = row.get("error", "")
    if err is None:
        return ""
    return str(err).strip().lower()


def classify_row(
    row: dict,
    *,
    provenance_threshold: float = 0.80,
    field_f1_threshold: float = 0.85,
    latency_threshold_seconds: float = 120.0,
) -> list[str]:
    """
    Classify one scored task row into one or more failure categories.

    One task can have multiple errors.
    Example: schema_violation + missing_records + bad_provenance
    """
    errors: list[str] = []

    err = _error_text(row)

    runtime_success = _to_bool(row.get("runtime_success"))
    json_valid = _to_bool(row.get("json_valid"))

    num_pred = _to_float(row.get("num_predicted_records"))
    num_gold = _to_float(row.get("num_gold_records"))

    record_tp = _to_float(row.get("record_tp"))
    record_fp = _to_float(row.get("record_fp"))
    record_fn = _to_float(row.get("record_fn"))

    record_recall = _to_float(row.get("record_recall"))
    record_f1 = _to_float(row.get("record_f1"))

    # Prefer strict metric if Step 5 has been added.
    strict_field_f1 = _to_float(
        row.get("strict_field_f1", row.get("strict_micro_field_f1", row.get("field_f1")))
    )
    matched_field_f1 = _to_float(row.get("matched_field_f1", row.get("field_f1")))

    schema_adherence = _to_float(row.get("schema_adherence"))
    provenance_score = _to_float(row.get("provenance_score"))
    latency = _to_float(row.get("latency_seconds"))

    # 1. Missing prediction file
    if err == "missing_prediction":
        errors.append("missing_prediction")
        return errors

    # 2. Runtime / generation failure
    if not runtime_success:
        errors.append("runtime_error")

    # 3. Invalid JSON
    if not json_valid:
        errors.append("invalid_json")

    # 4. Empty extraction despite non-empty gold
    if num_gold > 0 and num_pred == 0:
        errors.append("empty_records")

    # 5. Schema violation
    if schema_adherence < 1.0:
        errors.append("schema_violation")

    # 6. Missing records
    if record_fn > 0:
        errors.append("missing_records")

    # 7. Extra / hallucinated records
    if record_fp > 0:
        errors.append("extra_records")

    # 8. Weak record alignment
    if num_gold > 0 and record_tp == 0 and num_pred > 0:
        errors.append("wrong_record_alignment")

    # 9. Wrong field values inside matched records
    if record_tp > 0 and matched_field_f1 < field_f1_threshold:
        errors.append("wrong_field_value")

    # 10. Strict field failure including missed/extra records
    if num_gold > 0 and strict_field_f1 < field_f1_threshold:
        errors.append("low_strict_field_f1")

    # 11. Provenance failure
    if provenance_score < provenance_threshold:
        errors.append("bad_provenance")

    # 12. Very low recall
    if num_gold > 0 and record_recall < 0.50:
        errors.append("low_record_recall")

    # 13. Very low full extraction quality
    if num_gold > 0 and record_f1 < 0.50:
        errors.append("low_record_f1")

    # 14. Slow run
    if latency > latency_threshold_seconds:
        errors.append("high_latency")

    # 15. Keep raw error message as category if present and not already covered
    if err and err not in {"none", "null", "missing_prediction"}:
        if "timeout" in err:
            errors.append("timeout")
        elif "rate" in err and "limit" in err:
            errors.append("rate_limit")
        elif "context" in err or "token" in err:
            errors.append("context_or_token_limit")
        elif "json" in err:
            errors.append("json_parse_error")
        else:
            errors.append("other_runtime_message")

    if not errors:
        errors.append("no_major_error")

    # Remove duplicates while preserving order
    unique_errors: list[str] = []
    seen: set[str] = set()
    for e in errors:
        if e not in seen:
            unique_errors.append(e)
            seen.add(e)

    return unique_errors


def classify_errors(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Aggregate error counts over all rows."""
    counts: Counter[str] = Counter()
    for row in rows:
        for error in classify_row(row):
            counts[error] += 1

    total_rows = len(rows)
    return {
        error: {
            "count": count,
            "rate": round(count / total_rows, 4) if total_rows else 0.0,
        }
        for error, count in sorted(counts.items())
    }


def taxonomy_rows(rows: list[dict], group_fields: list[str] | None = None) -> list[dict]:
    """
    Return CSV-ready taxonomy rows.

    If group_fields is None: one global failure-taxonomy table.
    If group_fields = ["baseline", "model"]: one table per baseline/model.
    """
    group_fields = group_fields or []

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    if group_fields:
        for row in rows:
            key = tuple(row.get(field, "") for field in group_fields)
            grouped[key].append(row)
    else:
        grouped[tuple()].extend(rows)

    output = []
    for key, group_rows in grouped.items():
        taxonomy = classify_errors(group_rows)
        for error_type, values in taxonomy.items():
            item: dict = {}
            for i, field in enumerate(group_fields):
                item[field] = key[i]
            item["error_type"] = error_type
            item["count"] = values["count"]
            item["rate"] = values["rate"]
            item["num_tasks"] = len(group_rows)
            output.append(item)

    return sorted(
        output,
        key=lambda x: tuple(str(x.get(g, "")) for g in group_fields)
        + (-float(x.get("count", 0)), str(x.get("error_type", ""))),
    )


def add_error_labels(rows: list[dict]) -> list[dict]:
    """
    Add an error_labels column to each per-task row.
    Useful for manual inspection and paper error analysis.
    """
    labeled = []
    for row in rows:
        new_row = dict(row)
        new_row["error_labels"] = ";".join(classify_row(row))
        labeled.append(new_row)
    return labeled
