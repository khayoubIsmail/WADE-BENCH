from __future__ import annotations

from typing import Any, Dict


def required_fields(schema: Dict[str, Any]) -> set[str]:
    if isinstance(schema.get("required_fields"), list):
        return set(schema["required_fields"])
    if isinstance(schema.get("required"), list):
        return set(schema["required"])
    fields = schema.get("fields")
    if isinstance(fields, dict):
        return {k for k, v in fields.items() if isinstance(v, dict) and v.get("required")}
    return set()


def validate_prediction_schema(prediction: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    records = prediction.get("records")
    if not isinstance(records, list):
        return False, ["prediction.records must be a list"]
    req = required_fields(schema)
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"records[{i}] is not an object")
            continue
        fields = record.get("fields")
        if not isinstance(fields, dict):
            errors.append(f"records[{i}].fields is missing or not an object")
            continue
        missing = sorted(req - set(fields.keys()))
        if missing:
            errors.append(f"records[{i}] missing required fields: {missing}")
    return len(errors) == 0, errors
