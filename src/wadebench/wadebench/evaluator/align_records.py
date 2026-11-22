"""
align_records.py — Record alignment between predicted and gold records.

Priority order for matching:
  1. URL match (product_url, event_url, tender_url, etc.)
  2. Exact title/name match
  3. Normalized fuzzy title/name match
  4. Field-overlap similarity
"""

import re
import unicodedata
from typing import List, Dict, Any, Tuple, Optional


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace, remove punctuation."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Strip accents
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_field_value(record: Dict[str, Any], field_name: str) -> Optional[str]:
    """
    Extract a field value from a record, handling both flat and nested formats.

    Gold format:   {"fields": {"product_name": {"value": "...", "normalized": "..."}}}
    Predicted fmt: {"product_name": "..."} or same as gold
    """
    # Nested gold format
    fields = record.get("fields", {})
    if field_name in fields:
        entry = fields[field_name]
        if isinstance(entry, dict):
            return entry.get("normalized") or entry.get("value")
        return entry

    # Flat predicted format
    if field_name in record:
        return record[field_name]

    return None


_URL_FIELDS = [
    "product_url",
    "event_url",
    "tender_url",
    "job_url",
    "listing_url",
    "property_url",
    "apply_url",
    "url",
    "detail_url",
    "link",
    "page_url",
    "source_url",
]

_NAME_FIELDS = [
    "product_name",
    "event_name",
    "tender_title",
    "job_title",
    "listing_title",
    "property_title",
    "address",
    "title",
    "name",
    "conference_name",
    "notice_heading",
]


def _get_url(record: Dict[str, Any]) -> Optional[str]:
    for f in _URL_FIELDS:
        v = _extract_field_value(record, f)
        if v and isinstance(v, str) and v.startswith("http"):
            return v.rstrip("/").lower()
    return None


def _get_name(record: Dict[str, Any]) -> Optional[str]:
    for f in _NAME_FIELDS:
        v = _extract_field_value(record, f)
        if v and isinstance(v, str) and len(v) > 0:
            return v
    return None


def _field_overlap_score(pred: Dict[str, Any], gold: Dict[str, Any]) -> float:
    """Compute a simple Jaccard-style overlap of non-null field values."""
    pred_fields = pred.get("fields", pred)
    gold_fields = gold.get("fields", gold)

    if isinstance(pred_fields, dict) and isinstance(gold_fields, dict):
        # Collect keys that have non-null values in both
        all_keys = set()
        for k, v in gold_fields.items():
            val = v.get("value") if isinstance(v, dict) else v
            if val is not None:
                all_keys.add(k)

        if not all_keys:
            return 0.0

        matches = 0
        for k in all_keys:
            pred_val = _extract_field_value(pred, k)
            gold_val = _extract_field_value(gold, k)
            if pred_val is not None and gold_val is not None:
                if _normalize_text(str(pred_val)) == _normalize_text(str(gold_val)):
                    matches += 1

        return matches / len(all_keys)

    return 0.0


# ---------------------------------------------------------------------------
# Main alignment function
# ---------------------------------------------------------------------------

def align(
    predicted_records: List[Dict[str, Any]],
    gold_records: List[Dict[str, Any]],
) -> List[Tuple[Optional[Dict], Optional[Dict]]]:
    """
    Greedily match predicted records to gold records.

    Returns a list of (predicted, gold) tuples:
      - (pred, gold) = matched pair
      - (pred, None)  = false positive (unmatched prediction)
      - (None, gold)  = false negative (missed gold record)
    """
    if not gold_records:
        return [(p, None) for p in predicted_records]
    if not predicted_records:
        return [(None, g) for g in gold_records]

    used_gold = set()
    pairs: List[Tuple[Optional[Dict], Optional[Dict]]] = []

    # Pass 1: URL exact match
    for pi, pred in enumerate(predicted_records):
        pred_url = _get_url(pred)
        if not pred_url:
            continue
        for gi, gold in enumerate(gold_records):
            if gi in used_gold:
                continue
            gold_url = _get_url(gold)
            if gold_url and pred_url == gold_url:
                pairs.append((pred, gold))
                used_gold.add(gi)
                break

    matched_preds = {id(p) for p, g in pairs if p is not None}

    # Pass 2: Exact name match
    for pi, pred in enumerate(predicted_records):
        if id(pred) in matched_preds:
            continue
        pred_name = _get_name(pred)
        if not pred_name:
            continue
        for gi, gold in enumerate(gold_records):
            if gi in used_gold:
                continue
            gold_name = _get_name(gold)
            if gold_name and pred_name.strip() == gold_name.strip():
                pairs.append((pred, gold))
                used_gold.add(gi)
                matched_preds.add(id(pred))
                break

    # Pass 3: Normalized fuzzy name match
    for pi, pred in enumerate(predicted_records):
        if id(pred) in matched_preds:
            continue
        pred_name = _get_name(pred)
        if not pred_name:
            continue
        norm_pred = _normalize_text(pred_name)
        if not norm_pred:
            continue
        for gi, gold in enumerate(gold_records):
            if gi in used_gold:
                continue
            gold_name = _get_name(gold)
            if not gold_name:
                continue
            norm_gold = _normalize_text(gold_name)
            if norm_pred == norm_gold:
                pairs.append((pred, gold))
                used_gold.add(gi)
                matched_preds.add(id(pred))
                break

    # Pass 4: Best field-overlap similarity (threshold = 0.5)
    remaining_preds = [p for p in predicted_records if id(p) not in matched_preds]
    remaining_gold_indices = [gi for gi in range(len(gold_records)) if gi not in used_gold]

    for pred in remaining_preds:
        best_score = 0.0
        best_gi = None
        for gi in remaining_gold_indices:
            score = _field_overlap_score(pred, gold_records[gi])
            if score > best_score:
                best_score = score
                best_gi = gi
        if best_gi is not None and best_score >= 0.5:
            pairs.append((pred, gold_records[best_gi]))
            used_gold.add(best_gi)
            remaining_gold_indices.remove(best_gi)
        else:
            pairs.append((pred, None))  # false positive

    # Remaining unmatched gold = false negatives
    for gi in range(len(gold_records)):
        if gi not in used_gold:
            pairs.append((None, gold_records[gi]))

    return pairs
