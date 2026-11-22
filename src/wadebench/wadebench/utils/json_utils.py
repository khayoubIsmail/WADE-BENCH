from __future__ import annotations

import json
import re
from typing import Any

try:
    import json_repair as _json_repair
    _HAS_JSON_REPAIR = True
except ImportError:
    _HAS_JSON_REPAIR = False


def _clean_json_text(text: str) -> str:
    text = text.strip()
    # Strip <think>...</think> blocks produced by reasoning/thinking models (e.g. Gemma 4, Qwen3).
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Also strip unclosed <think> tags (model cut off mid-thought).
    text = re.sub(r"<think>.*", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    # Strip markdown code blocks globally in case the model adds conversational text
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    # NOTE: Do NOT strip // here — URLs like https://... contain // and would be destroyed.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text.strip()


def _try_truncate_to_valid(candidate: str) -> dict | None:
    # Try to recover common truncated outputs by closing the records array/object.
    for suffix in ["}]}", "]}", "}"]:
        try:
            return json.loads(candidate.rstrip() + suffix)
        except json.JSONDecodeError:
            pass

    # Walk backwards to find the last complete record and salvage partial output.
    # This handles the common case where JSON is cut off inside a string value
    # (e.g., a long text_quote in provenance) — find the last closed sibling
    # object and close the remaining open structures.
    text = candidate.rstrip()
    last_complete = text.rfind("},")
    while last_complete != -1:
        truncated = text[: last_complete + 1]
        # Try increasingly aggressive closings: the cut might be inside provenance
        # (needs record-close + array + outer) or at record boundary.
        for suffix in ["}]}", "]}", "}"]:
            try:
                return json.loads(truncated + suffix)
            except json.JSONDecodeError:
                pass
        last_complete = text.rfind("},", 0, last_complete)

    return None


def _try_json_repair(candidate: str) -> dict | None:
    """Last-resort repair using json_repair library.

    Handles missing commas, unescaped quotes, mixed array/object syntax,
    and other malformed JSON that the manual truncation logic cannot fix.
    Returns None if json_repair is not installed or the result is not a dict.
    """
    if not _HAS_JSON_REPAIR:
        return None
    try:
        result = _json_repair.loads(candidate)
        if isinstance(result, dict):
            return result
        # json_repair may return a list; wrap it
        if isinstance(result, list):
            return {"records": result}
        return None
    except Exception:
        return None

def extract_json_object(text: str) -> dict:
    if not text:
        raise ValueError("Empty model output")

    # Try parsing the raw text first — before any cleaning that might corrupt URLs
    # (e.g. // in https:// being stripped by comment-removal regexes).
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    cleaned = _clean_json_text(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        recovered = _try_truncate_to_valid(candidate)
        if recovered is not None:
            return recovered

    # Last resort: use json_repair library for deeply malformed output
    # (missing commas, unescaped quotes, mixed syntax, etc.)
    repaired = _try_json_repair(cleaned)
    if repaired is not None:
        return repaired

    raise ValueError("No valid JSON object found in model output")



def normalize_prediction_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"records": []}
    if "records" not in payload or not isinstance(payload.get("records"), list):
        payload["records"] = []
    # Enforce record wrapper shape and stable record IDs.
    normalized_records = []
    for i, record in enumerate(payload["records"], start=1):
        if not isinstance(record, dict):
            continue
        if "fields" not in record or not isinstance(record.get("fields"), dict):
            metadata_keys = {"record_id", "provenance", "run_metadata", "baseline", "model", "task_id", "domain", "schema_id"}
            fields = {k: v for k, v in record.items() if k not in metadata_keys}
            record = {
                "record_id": record.get("record_id") or f"pred_{i:03d}",
                "fields": fields,
                "provenance": record.get("provenance", {}),
            }
        else:
            record.setdefault("record_id", f"pred_{i:03d}")
            record.setdefault("provenance", {})
        normalized_records.append(record)
    payload["records"] = normalized_records
    return payload


def normalize_null_strings(obj: Any):
    if isinstance(obj, dict):
        return {k: normalize_null_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_null_strings(v) for v in obj]
    if isinstance(obj, str) and obj.strip().lower() in {"null", "none", "n/a", "na", "not available", "unknown", ""}:
        return None
    return obj


def _field_value(v: Any) -> Any:
    if isinstance(v, dict) and "value" in v:
        return v.get("value")
    return v


def is_empty_record(record: dict) -> bool:
    if not isinstance(record, dict):
        return True
    fields = record.get("fields", {})
    if not isinstance(fields, dict) or not fields:
        return True
    for v in fields.values():
        val = _field_value(v)
        if val is not None and str(val).strip() != "":
            return False
    return True


def remove_empty_records(payload: dict) -> dict:
    records = payload.get("records", [])
    payload["records"] = [r for r in records if not is_empty_record(r)]
    return payload


def normalize_prediction(payload: dict) -> dict:
    payload = normalize_null_strings(payload)
    payload = normalize_prediction_payload(payload)
    payload = remove_empty_records(payload)
    return payload
