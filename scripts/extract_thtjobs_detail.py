import json
import sys
import re
from datetime import datetime
from lxml import html

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'https://www.timeshighereducation.com'

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

with open('data/raw_snapshots/jobs/timeshighered_detail/page.html', 'rb') as f:
    parser = html.HTMLParser(encoding='utf-8')
    tree = html.fromstring(f.read(), parser=parser)

record = {
    "gold_record_id": "WBV1_JOBS_THTJOBS_002_DETAIL_001",
    "fields": {},
    "provenance": {}
}

def set_field(key, val, node, normalized_val=None):
    if normalized_val is None:
        normalized_val = val
    record["fields"][key] = {"value": val, "normalized": normalized_val}
    if val is None or val == [] or val == {}:
        return
    if isinstance(val, str):
        text_quote = val[:50]
    elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
        text_quote = val[0][:50]
    else:
        text_quote = None
    if node is not None:
        record["provenance"][key] = {
            "snapshot_id": "timeshighered_detail",
            "css_selector": get_css(node),
            "xpath": get_xpath(node),
            "text_quote": text_quote
        }

# ── Job title ──────────────────────────────────────────────
h1 = tree.xpath('//h1[contains(@class, "mds-font-s6")]')
if h1:
    set_field("job_title", h1[0].text_content().strip(), h1[0])

# ── Job URL (canonical link in <head>) ────────────────────
canonical = tree.xpath('//link[@rel="canonical"]')
if canonical:
    set_field("job_url", canonical[0].get('href'), canonical[0])
else:
    # Fallback: base href
    base = tree.xpath('//base')
    if base:
        set_field("job_url", base[0].get('href'), base[0])

# ── Logo ──────────────────────────────────────────────────
logo_img = tree.xpath('//img[contains(@class, "logo")]')
if logo_img:
    src = logo_img[0].get('src', '')
    if src.startswith('/'):
        src = BASE_URL + src
    set_field("logo", src, logo_img[0])

# ── DL key/value pairs ────────────────────────────────────
dt_nodes = tree.xpath('//dl[contains(@class, "mds-list--definition")]//dt')
dd_nodes = tree.xpath('//dl[contains(@class, "mds-list--definition")]//dd')
dl_map = {dt.text_content().strip(): (dt, dd) for dt, dd in zip(dt_nodes, dd_nodes)}

# Employer / company
if 'Employer' in dl_map:
    dt, dd = dl_map['Employer']
    set_field("company", dd.text_content().strip(), dd)

# Location
if 'Location' in dl_map:
    dt, dd = dl_map['Location']
    set_field("location", dd.text_content().strip(), dd)

# Closing date (normalized to YYYY-MM-DD)
if 'Closing date' in dl_map:
    dt, dd = dl_map['Closing date']
    raw_date = dd.text_content().strip()
    norm_date = raw_date
    try:
        dt_parsed = datetime.strptime(raw_date, "%d %b %Y")
        norm_date = dt_parsed.strftime("%Y-%m-%d")
    except ValueError:
        pass
    set_field("closing_date", raw_date, dd, normalized_val=norm_date)

# ── Apply URL ─────────────────────────────────────────────
apply_btn = tree.xpath('//*[@data-hook="apply-button"]')
if apply_btn:
    href = apply_btn[0].get('href', '')
    if href.startswith('/'):
        href = BASE_URL + href
    set_field("apply_url", href, apply_btn[0])

# ── Job type / employment type ────────────────────────────
# Inside the accordion – multiple dd values separated by dt keys
accordion_dts = tree.xpath('//details//dt')
accordion_dds = tree.xpath('//details//dd')
acc_map = {}
for dt, dd in zip(accordion_dts, accordion_dds):
    key = dt.text_content().strip()
    vals = [v.strip() for v in dd.text_content().split(',') if v.strip()]
    acc_map[key] = (dt, dd, vals)

if 'Job Type' in acc_map:
    _, dd, vals = acc_map['Job Type']
    set_field("job_type", vals, dd)

if 'Contract Type' in acc_map:
    _, dd, vals = acc_map['Contract Type']
    set_field("contract_type", vals[0] if vals else None, dd)

if 'Hours' in acc_map:
    _, dd, vals = acc_map['Hours']
    set_field("hours", vals[0] if vals else None, dd)

if 'Academic Discipline' in acc_map:
    _, dd, vals = acc_map['Academic Discipline']
    set_field("academic_discipline", vals, dd)

# ── Job description body ──────────────────────────────────
desc_node = tree.xpath('//div[contains(@class, "enhanced-job")]//div[contains(@class, "mds-surface__inner") and not(contains(@class, "mds-border-bottom"))]')
if desc_node:
    desc_text = desc_node[0].text_content().strip()
    # Clean up excess whitespace
    desc_text = re.sub(r'\s{3,}', '\n\n', desc_text)
    set_field("job_description", desc_text, desc_node[0])

# ── Print summary ─────────────────────────────────────────
print("Fields extracted:")
for k, v in record["fields"].items():
    val = v['value']
    print(f"  {k}: {repr(str(val)[:70])}")

# ── Write output ──────────────────────────────────────────
with open('data/gold/by_task/jobs/WBV1_JOBS_THTJOBS_002_DETAIL.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data["records"] = [record]
data["annotation_metadata"]["total_records_extracted"] = 1

with open('data/gold/by_task/jobs/WBV1_JOBS_THTJOBS_002_DETAIL.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nExtraction complete.")
