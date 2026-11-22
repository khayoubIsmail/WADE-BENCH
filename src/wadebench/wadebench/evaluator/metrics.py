from __future__ import annotations

import datetime
import re
from collections import Counter
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Value normalization
# ---------------------------------------------------------------------------

def normalize_value(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, dict) and "value" in val:
        val = val.get("value")
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, (int, float)):
        if isinstance(val, float) and val == int(val):
            return str(int(val))
        return str(val)
    if not isinstance(val, str):
        return str(val).strip().lower()

    s = val.strip()
    if not s or s.lower() in {"null", "none", "n/a", "na", "unknown", "not available"}:
        return None

    # Normalize URLs.
    if s.startswith("http://") or s.startswith("https://"):
        return s.rstrip("/").lower()

    # Normalize price-like strings.
    # Accept both symbol/code prefix and suffix forms:
    #   "$220", "220 USD", "USD 220", "USD220", "EUR 1,200.00".
    currency_codes = r"USD|EUR|GBP|EGP|MAD|DZD|SAR|AED|CAD|AUD|JPY|CNY|RMB|CHF|TRY|DH|DHS"
    stripped = s.strip()
    stripped = re.sub(rf"^\s*(?:{currency_codes})\s*", "", stripped, flags=re.I).strip()
    stripped = re.sub(r"^\s*(?:US|CA|AU)?\$\s*", "", stripped, flags=re.I).strip()
    stripped = stripped.lstrip("£€$¥₹ ").strip()
    stripped = re.sub(rf"\s*(?:{currency_codes})\s*$", "", stripped, flags=re.I).strip()
    if stripped != s and re.match(r"^[\d,]+(?:\.\d+)?$", stripped):
        return _normalize_number_string(stripped.replace(",", ""))
    if re.match(r"^[\d,]+(?:\.\d+)?$", s):
        return _normalize_number_string(s.replace(",", ""))

    normalized_date = _try_normalize_date(s)
    if normalized_date:
        return normalized_date

    return re.sub(r"\s+", " ", s.lower()).strip()


def _normalize_number_string(s: str) -> str:
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return str(f).rstrip("0").rstrip(".")
    except Exception:
        return s


def _try_normalize_date(s: str) -> Optional[str]:
    formats = [
        "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
        "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(s.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    range_match = re.match(r"^(\w+ \d+)[–\-]\d+,\s*(\d{4})$", s.strip())
    if range_match:
        try:
            return datetime.datetime.strptime(f"{range_match.group(1)}, {range_match.group(2)}", "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# Schema adherence
# ---------------------------------------------------------------------------

def _required_fields(schema: Dict[str, Any]) -> set[str]:
    if not isinstance(schema, dict):
        return set()
    if isinstance(schema.get("required_fields"), list):
        return set(schema["required_fields"])
    if isinstance(schema.get("required"), list):
        return set(schema["required"])
    fields = schema.get("fields")
    if isinstance(fields, dict):
        return {k for k, v in fields.items() if isinstance(v, dict) and v.get("required")}
    return set()


def check_schema_adherence(prediction: Dict[str, Any], schema: Dict[str, Any], gold_records: Optional[list] = None) -> int:
    records = prediction.get("records")
    if not isinstance(records, list):
        return 0

    # Empty prediction is valid only for genuinely empty-gold tasks.
    if len(records) == 0:
        return 1 if gold_records is not None and len(gold_records) == 0 else 0

    required = _required_fields(schema)
    for record in records:
        if not isinstance(record, dict):
            return 0
        fields = record.get("fields", record)
        if not isinstance(fields, dict):
            return 0
        for req in required:
            if req not in fields:
                return 0
    return 1


# ---------------------------------------------------------------------------
# Field-level comparison
# ---------------------------------------------------------------------------

def _value(entry: Any) -> Any:
    if isinstance(entry, dict) and "value" in entry:
        return entry.get("value")
    return entry


METADATA_KEYS = {
    "gold_record_id",
    "record_id",
    "provenance",
    "run_metadata",
    "baseline",
    "model",
    "task_id",
    "domain",
    "schema_id",
}


def count_non_null_eval_fields(record: Dict[str, Any]) -> int:
    """
    Count non-null data fields in one record.

    Excludes metadata/provenance keys and counts only fields that
    should participate in extraction evaluation.
    """
    fields = record.get("fields", record)
    if not isinstance(fields, dict):
        return 0
    count = 0
    for key, value in fields.items():
        if key in METADATA_KEYS:
            continue
        if _value(value) is not None:
            count += 1
    return count


def _normalized_list_counter(values: list[Any]) -> Counter[str]:
    """Normalize list-valued fields as an order-insensitive multiset.

    This avoids unfairly penalizing correct list fields returned in a different
    order, while still respecting duplicates if a schema genuinely uses them.
    Null-like list items are ignored.
    """
    normalized_items = []
    for item in values:
        norm = normalize_value(item)
        if norm is not None:
            normalized_items.append(norm)
    return Counter(normalized_items)


def _values_match(pred_val: Any, gold_val: Any) -> bool:
    if isinstance(pred_val, list) and isinstance(gold_val, list):
        return _normalized_list_counter(pred_val) == _normalized_list_counter(gold_val)

    # Gracefully handle one-item list vs scalar, e.g. ["AI"] vs "AI".
    if isinstance(pred_val, list) and not isinstance(gold_val, list):
        return len(pred_val) == 1 and _values_match(pred_val[0], gold_val)
    if isinstance(gold_val, list) and not isinstance(pred_val, list):
        return len(gold_val) == 1 and _values_match(pred_val, gold_val[0])

    norm_p = normalize_value(pred_val)
    norm_g = normalize_value(gold_val)
    if norm_p is None and norm_g is None:
        return True
    if norm_p is None or norm_g is None:
        return False
    return norm_p == norm_g


def calculate_field_metrics(pred_record: Dict[str, Any], gold_record: Dict[str, Any]) -> Dict[str, float]:
    gold_fields = gold_record.get("fields", gold_record)
    pred_fields = pred_record.get("fields", pred_record)
    if not isinstance(gold_fields, dict) or not isinstance(pred_fields, dict):
        return {"field_precision": 0.0, "field_recall": 0.0, "field_f1": 0.0, "field_correct": 0, "field_predicted": 0, "field_gold": 0, "extra_fields": 0}

    metadata_keys = {"gold_record_id", "record_id", "provenance", "run_metadata", "baseline", "model", "task_id", "domain", "schema_id"}
    gold_keys = {k for k, v in gold_fields.items() if k not in METADATA_KEYS and _value(v) is not None}
    pred_keys = {k for k, v in pred_fields.items() if k not in METADATA_KEYS and _value(v) is not None}

    if not gold_keys:
        return {"field_precision": 1.0, "field_recall": 1.0, "field_f1": 1.0, "field_correct": 0, "field_predicted": len(pred_keys), "field_gold": 0, "extra_fields": len(pred_keys)}

    correct = 0
    for k in gold_keys:
        if k in pred_fields and _values_match(_value(pred_fields.get(k)), _value(gold_fields.get(k))):
            correct += 1

    extra_fields = len(pred_keys - set(gold_fields.keys()))
    precision_denom = len(pred_keys) if pred_keys else 0
    precision = correct / precision_denom if precision_denom else 0.0
    recall = correct / len(gold_keys) if gold_keys else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "field_precision": round(precision, 4),
        "field_recall": round(recall, 4),
        "field_f1": round(f1, 4),
        "field_correct": correct,
        "field_predicted": len(pred_keys),
        "field_gold": len(gold_keys),
        "extra_fields": extra_fields,
    }


def calculate_strict_field_metrics(pairs: list[tuple[Any, Any]]) -> Dict[str, float]:
    """
    Strict field-level micro metrics over the whole task.

    Difference from calculate_field_metrics (which operates per matched record):
    - matched records contribute correct/predicted/gold fields
    - false-positive records contribute predicted fields only (penalized)
    - false-negative records contribute gold fields only (penalized)

    This prevents artificially high field scores when only a subset of
    records is extracted correctly.
    """
    strict_correct = 0
    strict_predicted = 0
    strict_gold = 0

    for pred, gold in pairs:
        if pred is not None and gold is not None:
            # Matched record: count correct/predicted/gold normally
            fm = calculate_field_metrics(pred, gold)
            strict_correct += int(fm.get("field_correct", 0))
            strict_predicted += int(fm.get("field_predicted", 0))
            strict_gold += int(fm.get("field_gold", 0))
        elif pred is not None and gold is None:
            # Extra predicted record: all predicted fields are false positives
            strict_predicted += count_non_null_eval_fields(pred)
        elif pred is None and gold is not None:
            # Missed gold record: all gold fields are false negatives
            strict_gold += count_non_null_eval_fields(gold)

    if strict_predicted == 0 and strict_gold == 0:
        strict_precision = strict_recall = strict_f1 = 1.0
    else:
        strict_precision = strict_correct / strict_predicted if strict_predicted else 0.0
        strict_recall = strict_correct / strict_gold if strict_gold else 0.0
        strict_f1 = (
            2 * strict_precision * strict_recall / (strict_precision + strict_recall)
            if (strict_precision + strict_recall)
            else 0.0
        )

    return {
        "strict_field_correct": strict_correct,
        "strict_field_predicted": strict_predicted,
        "strict_field_gold": strict_gold,
        "strict_field_precision": round(strict_precision, 4),
        "strict_field_recall": round(strict_recall, 4),
        "strict_field_f1": round(strict_f1, 4),
        # Alias for paper clarity
        "strict_micro_field_f1": round(strict_f1, 4),
    }
