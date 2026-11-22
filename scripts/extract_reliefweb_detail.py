import json
import os
from datetime import datetime
from lxml import html


def get_xpath(node):
    return node.getroottree().getpath(node)


def get_css(node):
    path = []
    for anc in node.xpath('ancestor-or-self::*'):
        if anc.tag == 'html':
            continue
        step = anc.tag
        if anc.get('id'):
            step += '#' + anc.get('id')
            path = [step]
            continue
        siblings = anc.xpath(f'preceding-sibling::{anc.tag}')
        if siblings or anc.xpath(f'following-sibling::{anc.tag}'):
            step += f':nth-of-type({len(siblings) + 1})'
        path.append(step)
    return ' > '.join(path)


def normalize_date(raw: str) -> str:
    """Convert '11 Jun 2026' -> '2026-06-11'. Returns raw string on failure."""
    for fmt in ("%d %b %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


with open('data/raw_snapshots/jobs/reliefweb_detail/page.html', 'r', encoding='utf-8') as f:
    tree = html.fromstring(f.read())


record = {
    "gold_record_id": "WBV1_JOBS_RELIEFWEB_002_DETAIL_001",
    "fields": {},
    "provenance": {},
    "notes": "Extracted via script"
}


# ── 1. job_title ──────────────────────────────────────────────────────────────
title_nodes = tree.xpath('//article//header//h1')
if title_nodes:
    n = title_nodes[0]
    val = n.text_content().strip()
    record["fields"]["job_title"] = {"value": val, "normalized": val}
    record["provenance"]["job_title"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(n),
        "xpath": get_xpath(n),
        "text_quote": val
    }


# ── 2. job_url (canonical href in <head>) ─────────────────────────────────────
canonical = tree.xpath('//link[@rel="canonical"]')
if canonical:
    n = canonical[0]
    val = n.get('href')
    record["fields"]["job_url"] = {"value": val, "normalized": val}
    record["provenance"]["job_url"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(n),
        "xpath": get_xpath(n),
        "text_quote": None
    }


# ── 3. organization (Source dd) ───────────────────────────────────────────────
org_nodes = tree.xpath('//article//header//dl//dd[1]//a | //article//header//dl//dd[1]')
if org_nodes:
    # Prefer the <a> link text if present
    a_nodes = tree.xpath('//article//header//dl//dd[1]//a')
    n = a_nodes[0] if a_nodes else tree.xpath('//article//header//dl//dd[1]')[0]
    val = n.text_content().strip()
    record["fields"]["organization"] = {"value": val, "normalized": val}
    record["provenance"]["organization"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(n),
        "xpath": get_xpath(n),
        "text_quote": val
    }


# ── 4. posted_date ────────────────────────────────────────────────────────────
posted_nodes = tree.xpath('//article//header//dl//dd//time[@class and contains(@class,"posted")] | //article//header//dl//dd[2]//time | //article//header//dl//dd[2]')
if posted_nodes:
    n = posted_nodes[0]
    # Try <time datetime> attribute first
    val = n.get('datetime') or n.text_content().strip()
    norm = normalize_date(val)
    record["fields"]["posted_date"] = {"value": val, "normalized": norm}
    record["provenance"]["posted_date"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(n),
        "xpath": get_xpath(n),
        "text_quote": val
    }


# ── 5. closing_date ───────────────────────────────────────────────────────────
closing_nodes = tree.xpath('//article//header//dl//dd[3]//time | //article//header//dl//dd[3]')
if closing_nodes:
    n = closing_nodes[0]
    val = n.get('datetime') or n.text_content().strip()
    norm = normalize_date(val)
    record["fields"]["closing_date"] = {"value": val, "normalized": norm}
    record["provenance"]["closing_date"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(n),
        "xpath": get_xpath(n),
        "text_quote": val
    }


# ── 6. location ───────────────────────────────────────────────────────────────
loc_dt = tree.xpath('//section[@id="details"]//dt[normalize-space(text())="Country"]')
if loc_dt:
    n = loc_dt[0].getnext()
    if n is not None:
        a_nodes = n.xpath('.//a')
        target = a_nodes[0] if a_nodes else n
        val = target.text_content().strip()
        record["fields"]["location"] = {"value": val, "normalized": val}
        record["provenance"]["location"] = {
            "snapshot_id": "reliefweb_detail",
            "css_selector": get_css(target),
            "xpath": get_xpath(target),
            "text_quote": val
        }


# ── 7. years_of_experience ────────────────────────────────────────────────────
yoe_dt = tree.xpath('//section[@id="details"]//dt[normalize-space(text())="Years of experience"]')
if yoe_dt:
    n = yoe_dt[0].getnext()
    if n is not None:
        a_nodes = n.xpath('.//a')
        target = a_nodes[0] if a_nodes else n
        val = target.text_content().strip()
        record["fields"]["years_of_experience"] = {"value": val, "normalized": val}
        record["provenance"]["years_of_experience"] = {
            "snapshot_id": "reliefweb_detail",
            "css_selector": get_css(target),
            "xpath": get_xpath(target),
            "text_quote": val
        }


# ── 8. theme ──────────────────────────────────────────────────────────────────
theme_dt = tree.xpath('//section[@id="details"]//dt[normalize-space(text())="Theme"]')
if theme_dt:
    n = theme_dt[0].getnext()
    if n is not None:
        a_nodes = n.xpath('.//a')
        target = a_nodes[0] if a_nodes else n
        val = target.text_content().strip()
        record["fields"]["theme"] = {"value": val, "normalized": val}
        record["provenance"]["theme"] = {
            "snapshot_id": "reliefweb_detail",
            "css_selector": get_css(target),
            "xpath": get_xpath(target),
            "text_quote": val
        }


# ── 9. apply_url ──────────────────────────────────────────────────────────────
# "How to apply" section → first <a> link
apply_sections = tree.xpath('//section[.//h2[normalize-space(text())="How to apply"] or .//h3[normalize-space(text())="How to apply"] or .//h4[normalize-space(text())="How to apply"]]')
if apply_sections:
    apply_links = apply_sections[0].xpath('.//a[@href]')
    # Pick first link that is NOT an internal reliefweb link
    for a in apply_links:
        href = a.get('href', '')
        if href and 'reliefweb.int' not in href and 'datenschutz' not in href.lower() and 'privacy' not in href.lower():
            val = href
            record["fields"]["apply_url"] = {"value": val, "normalized": val}
            record["provenance"]["apply_url"] = {
                "snapshot_id": "reliefweb_detail",
                "css_selector": get_css(a),
                "xpath": get_xpath(a),
                "text_quote": None
            }
            break


# ── 10. job_description ──────────────────────────────────────────────────────
# Full text of article > div.rw-article__content, excluding 'How to apply' section
content_divs = tree.xpath('//article/div[contains(@class,"rw-article__content")]')
if content_divs:
    n = content_divs[0]
    # Remove the 'How to apply' section from a copy to get pure description
    from copy import deepcopy
    from lxml import etree
    content_copy = deepcopy(n)
    for apply_sec in content_copy.xpath('.//section'):
        h = apply_sec.xpath('.//h2 | .//h3 | .//h4')
        for heading in h:
            if 'apply' in heading.text_content().lower():
                apply_sec.getparent().remove(apply_sec)
                break
    val = content_copy.text_content().strip()
    record["fields"]["job_description"] = {"value": val, "normalized": val}
    record["provenance"]["job_description"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(n),
        "xpath": get_xpath(n),
        "text_quote": val[:80]
    }


# ── 11. what_we_offer ────────────────────────────────────────────────────────
# Find <p><strong>What we offer</strong></p> then collect the next sibling <ol>/<ul>
offer_p = tree.xpath('//p[strong[contains(text(), "offer")]]')
if offer_p:
    p = offer_p[0]
    nxt = p.getnext()
    offer_items = []
    while nxt is not None and nxt.tag in ('ul', 'ol', 'p'):
        # Extract individual <li> items if it's a list
        lis = nxt.xpath('.//li')
        if lis:
            for li in lis:
                text = li.text_content().strip()
                if text:
                    offer_items.append(text)
        else:
            text = nxt.text_content().strip()
            if text:
                offer_items.append(text)
        nxt = nxt.getnext()
    # For provenance, point to the first sibling list/paragraph
    target_node = p.getnext() if p.getnext() is not None else p
    record["fields"]["what_we_offer"] = {"value": offer_items, "normalized": offer_items}
    record["provenance"]["what_we_offer"] = {
        "snapshot_id": "reliefweb_detail",
        "css_selector": get_css(target_node),
        "xpath": get_xpath(target_node),
        "text_quote": offer_items[0] if offer_items else None
    }


# ── Write output ──────────────────────────────────────────────────────────────
with open('data/gold/by_task/jobs/WBV1_JOBS_RELIEFWEB_002_DETAIL.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['records'] = [record]
data['annotation_metadata']['total_records_extracted'] = 1

with open('data/gold/by_task/jobs/WBV1_JOBS_RELIEFWEB_002_DETAIL.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Fields extracted:")
for k, v in record['fields'].items():
    val_preview = str(v['value'])[:60] if v['value'] else 'null'
    print(f"  {k}: {val_preview}")
