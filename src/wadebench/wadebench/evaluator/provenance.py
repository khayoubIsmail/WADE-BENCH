from __future__ import annotations

from typing import Dict, Any

_VALID_BY_BASELINE = {
    "b1_html_llm": {"page.html"},
    "b1": {"page.html"},
    "b2_markdown_llm": {"page.markdown.md"},
    "b2": {"page.markdown.md"},
    "b3_vision_llm": {"screenshot.png"},
    "b3": {"screenshot.png"},
    "b4_playwright_mcp_agent": {"page.safe.html", "page.html", "text.txt", "ax_tree.json", "metadata.json"},
    "b4": {"page.safe.html", "page.html", "text.txt", "ax_tree.json", "metadata.json"},
    # R1-2 reviewer experiment: DOM-based agents reading frozen snapshots via local server.
    # Valid sources are the same frozen files as B4 (index.html plays the role of page.html).
    "r1_agent": {"index.html", "page.safe.html", "page.html", "text.txt",
                 "ax_tree.json", "accessibility_tree.json", "metadata.json", "visible_text.txt"},
}

_METADATA_KEYS = {"record_id", "gold_record_id", "provenance", "baseline", "model", "task_id", "domain", "schema_id", "run_metadata"}


def _valid_sources(baseline: str) -> set[str]:
    return _VALID_BY_BASELINE.get((baseline or "").lower(), set().union(*_VALID_BY_BASELINE.values()))


def _is_valid_source(source: str, baseline: str) -> bool:
    return isinstance(source, str) and source.lower().strip() in _valid_sources(baseline)


def _extract_field_provenance(record: Dict[str, Any], field_name: str) -> Dict[str, Any] | None:
    fields = record.get("fields", {})
    if isinstance(fields, dict):
        field_entry = fields.get(field_name)
        if isinstance(field_entry, dict) and isinstance(field_entry.get("provenance"), dict):
            return field_entry["provenance"]

    prov = record.get("provenance")
    if not isinstance(prov, dict):
        return None

    # Preferred field-level format: provenance[field_name] = {...}
    field_prov = prov.get(field_name)
    if isinstance(field_prov, dict):
        return field_prov

    # Backward-compatible record-level provenance.
    if any(k in prov for k in (
        "source",
        "text_quote",
        "css_selector",
        "xpath",
        "css_selector_absolute",
        "xpath_absolute",
        "bbox",
    )):
        return prov
    return None


def _selector_flags(prov: Dict[str, Any]) -> tuple[bool, bool, bool]:
    """Return semantic, absolute, any selector evidence flags."""
    if not isinstance(prov, dict):
        return False, False, False
    has_semantic = bool(prov.get("css_selector") or prov.get("xpath"))
    has_absolute = bool(prov.get("css_selector_absolute") or prov.get("xpath_absolute"))
    return has_semantic, has_absolute, (has_semantic or has_absolute)


def _score_one_provenance(prov: Dict[str, Any], baseline: str) -> tuple[float, bool, bool, bool, bool]:
    """
    Score field-level provenance.

    The core provenance signal is a valid frozen-source reference plus a supporting quote.
    Selectors are reported separately, with semantic selectors preferred over absolute
    selectors. Absolute selectors are useful fallback evidence but should not be treated
    as equivalent to robust semantic selectors in paper analysis.
    """
    if not isinstance(prov, dict):
        return 0.0, False, False, False, False
    source = prov.get("source")
    if not _is_valid_source(source, baseline):
        return 0.0, False, False, False, False

    quote = prov.get("text_quote")
    has_quote = isinstance(quote, str) and len(quote.strip()) > 5
    has_semantic_selector, has_absolute_selector, has_any_selector = _selector_flags(prov)

    # Base score: valid source + supporting quote.
    # Small selector bonus distinguishes stronger/locatable provenance.
    score = 0.5
    if has_quote:
        score += 0.35
    if has_semantic_selector:
        score += 0.15
    elif has_absolute_selector:
        score += 0.08
    score = min(score, 1.0)
    return score, has_quote, has_semantic_selector, has_absolute_selector, has_any_selector


def score_provenance_details(pred_records: list[dict[str, Any]], baseline: str) -> dict[str, Any]:
    total_fields = 0
    scored_fields = 0
    quote_fields = 0
    semantic_selector_fields = 0
    absolute_selector_fields = 0
    any_selector_fields = 0
    score_sum = 0.0

    for record in pred_records or []:
        fields = record.get("fields", record)
        if not isinstance(fields, dict):
            continue
        for field_name, value in fields.items():
            if field_name in _METADATA_KEYS:
                continue
            # Only require provenance for non-null predicted values.
            if isinstance(value, dict) and "value" in value:
                raw_value = value.get("value")
            else:
                raw_value = value
            if raw_value is None:
                continue
            total_fields += 1
            prov = _extract_field_provenance(record, field_name)
            score, has_quote, has_semantic_selector, has_absolute_selector, has_any_selector = _score_one_provenance(prov or {}, baseline)
            if score > 0:
                scored_fields += 1
            if has_quote:
                quote_fields += 1
            if has_semantic_selector:
                semantic_selector_fields += 1
            if has_absolute_selector:
                absolute_selector_fields += 1
            if has_any_selector:
                any_selector_fields += 1
            score_sum += score

    return {
        "provenance_score": round(score_sum / total_fields, 4) if total_fields else 0.0,
        "provenance_field_coverage": round(scored_fields / total_fields, 4) if total_fields else 0.0,
        "provenance_quote_coverage": round(quote_fields / total_fields, 4) if total_fields else 0.0,
        "selector_coverage": round(any_selector_fields / total_fields, 4) if total_fields else 0.0,
        "semantic_selector_coverage": round(semantic_selector_fields / total_fields, 4) if total_fields else 0.0,
        "absolute_selector_coverage": round(absolute_selector_fields / total_fields, 4) if total_fields else 0.0,
        "provenance_fields_total": total_fields,
        "provenance_fields_with_valid_source": scored_fields,
        "provenance_fields_with_semantic_selector": semantic_selector_fields,
        "provenance_fields_with_absolute_selector": absolute_selector_fields,
        "provenance_fields_with_any_selector": any_selector_fields,
    }


def score_provenance_for_task(pred_records: list, baseline: str) -> float:
    return score_provenance_details(pred_records, baseline)["provenance_score"]
