from __future__ import annotations

from typing import Dict, Any, List

from .align_records import align
from .metrics import (
    check_schema_adherence,
    calculate_field_metrics,
    calculate_strict_field_metrics,
)
from .provenance import score_provenance_details


def _safe_mean(values: List[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def score_prediction(
    prediction: Dict[str, Any],
    gold_data: Dict[str, Any],
    schema: Dict[str, Any],
    baseline: str,
    *,
    task_success_record_recall: float = 0.90,
    task_success_field_f1: float = 0.85,
    require_schema_adherence: bool = True,
) -> Dict[str, Any]:
    task_id = prediction.get("task_id", "unknown")
    pred_records = prediction.get("records", [])
    gold_records = gold_data.get("records", [])

    schema_adherence = check_schema_adherence(prediction, schema, gold_records=gold_records)
    pairs = align(pred_records, gold_records)

    true_positives = [(p, g) for p, g in pairs if p is not None and g is not None]
    false_positives = [(p, g) for p, g in pairs if p is not None and g is None]
    false_negatives = [(p, g) for p, g in pairs if p is None and g is not None]

    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)

    record_precision = tp / (tp + fp) if (tp + fp) else (1.0 if not pred_records and not gold_records else 0.0)
    record_recall = tp / (tp + fn) if (tp + fn) else (1.0 if not pred_records and not gold_records else 0.0)
    record_f1 = 2 * record_precision * record_recall / (record_precision + record_recall) if (record_precision + record_recall) else 0.0

    field_precisions = []
    field_recalls = []
    field_f1s = []
    extra_fields = 0
    field_correct = 0
    field_predicted = 0
    field_gold = 0

    for pred, gold in true_positives:
        fm = calculate_field_metrics(pred, gold)
        field_precisions.append(fm["field_precision"])
        field_recalls.append(fm["field_recall"])
        field_f1s.append(fm["field_f1"])
        extra_fields += fm.get("extra_fields", 0)
        field_correct += fm.get("field_correct", 0)
        field_predicted += fm.get("field_predicted", 0)
        field_gold += fm.get("field_gold", 0)

    # Empty-gold/empty-pred task is fully correct at field level.
    if not gold_records and not pred_records:
        macro_field_precision = macro_field_recall = macro_field_f1 = 1.0
    else:
        macro_field_precision = _safe_mean(field_precisions)
        macro_field_recall = _safe_mean(field_recalls)
        macro_field_f1 = _safe_mean(field_f1s)

    strict_field_metrics = calculate_strict_field_metrics(pairs)

    provenance = score_provenance_details(pred_records, baseline)
    run_meta = prediction.get("run_metadata", {})

    task_success = (
        record_recall >= task_success_record_recall
        and strict_field_metrics["strict_field_f1"] >= task_success_field_f1
        and (schema_adherence == 1 if require_schema_adherence else True)
    )

    return {
        "task_id": task_id,
        "domain": prediction.get("domain", ""),
        "baseline": baseline,
        "model": prediction.get("model", ""),
        "schema_id": prediction.get("schema_id", ""),
        "num_predicted_records": len(pred_records),
        "num_gold_records": len(gold_records),
        "record_tp": tp,
        "record_fp": fp,
        "record_fn": fn,
        "record_precision": round(record_precision, 4),
        "record_recall": round(record_recall, 4),
        "record_f1": round(record_f1, 4),
        # Backward-compatible old metric: matched-record macro field score
        "field_precision": macro_field_precision,
        "field_recall": macro_field_recall,
        "field_f1": macro_field_f1,
        # Clearer names for the old metric
        "matched_field_precision": macro_field_precision,
        "matched_field_recall": macro_field_recall,
        "matched_field_f1": macro_field_f1,
        "field_correct": field_correct,
        "field_predicted": field_predicted,
        "field_gold": field_gold,
        "extra_fields": extra_fields,
        # New strict whole-task field metric
        **strict_field_metrics,
        "schema_adherence": schema_adherence,
        **provenance,
        "task_success": int(task_success),
        "task_success_record_recall_threshold": task_success_record_recall,
        "task_success_field_f1_threshold": task_success_field_f1,
        "runtime_success": bool(run_meta.get("runtime_success", run_meta.get("success", False))),
        "json_valid": bool(run_meta.get("json_valid", False)),
        "latency_seconds": run_meta.get("latency_seconds", 0),
        "input_tokens": run_meta.get("input_tokens", 0),
        "output_tokens": run_meta.get("output_tokens", 0),
        "total_tokens": run_meta.get("total_tokens", run_meta.get("input_tokens", 0) + run_meta.get("output_tokens", 0)),
        "repaired": bool(run_meta.get("repaired", False)),
        "error": run_meta.get("error"),
    }
