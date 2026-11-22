import json
import sys
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

BASE_URL = 'https://remoteok.com'

with open('data/raw_snapshots/jobs/remoteok_listing/page.html', 'r', encoding='utf-8') as f:
    tree = html.fromstring(f.read())

rows = tree.xpath('//tr[contains(@class,"job") and @id]')
print(f'Found {len(rows)} job rows', file=sys.stderr)

records = []

for i, row in enumerate(rows):
    job_id = row.get('data-id', row.get('id', '').replace('job-', ''))
    record_id = f'WBV1_JOBS_REMOTEOK_001_LISTING_{i+1:03d}'

    record = {
        "gold_record_id": record_id,
        "fields": {},
        "provenance": {},
        "notes": "Extracted via script"
    }

    # ── 1. job_title ──────────────────────────────────────────────────────────
    title_nodes = row.xpath('.//h2[@itemprop="title"] | .//h2')
    if title_nodes:
        n = title_nodes[0]
        val = n.text_content().strip()
        record["fields"]["job_title"] = {"value": val, "normalized": val}
        record["provenance"]["job_title"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(n),
            "xpath": get_xpath(n),
            "text_quote": val
        }

    # ── 2. job_url ────────────────────────────────────────────────────────────
    href = row.get('data-href') or row.get('data-url')
    if href:
        url_val = BASE_URL + href if href.startswith('/') else href
        # For provenance, find the first <a class="preventLink"> in td.image
        url_node = row.xpath('.//td[contains(@class,"image")]//a[@class="preventLink"]')
        if not url_node:
            url_node = row.xpath('.//td[contains(@class,"position")]//a[@class="preventLink"]')
        if url_node:
            prov_node = url_node[0]
        else:
            prov_node = row  # fallback
        record["fields"]["job_url"] = {"value": url_val, "normalized": url_val}
        record["provenance"]["job_url"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(prov_node),
            "xpath": get_xpath(prov_node),
            "text_quote": None
        }

    # ── 3. company ────────────────────────────────────────────────────────────
    company_nodes = row.xpath('.//h3[@itemprop="name"] | .//span[@itemprop="name"]')
    if company_nodes:
        n = company_nodes[0]
        val = n.text_content().strip()
        record["fields"]["company"] = {"value": val, "normalized": val}
        record["provenance"]["company"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(n),
            "xpath": get_xpath(n),
            "text_quote": val
        }
    else:
        # Fallback to data-company attribute
        val = row.get('data-company')
        if val:
            record["fields"]["company"] = {"value": val, "normalized": val}
            record["provenance"]["company"] = {
                "snapshot_id": "remoteok_listing",
                "css_selector": get_css(row),
                "xpath": get_xpath(row),
                "text_quote": val
            }

    # ── 4. logo ───────────────────────────────────────────────────────────────
    logo_nodes = row.xpath('.//td[contains(@class,"image")]//img')
    if logo_nodes:
        n = logo_nodes[0]
        val = n.get('src') or n.get('data-src')
        record["fields"]["logo"] = {"value": val, "normalized": val}
        record["provenance"]["logo"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(n),
            "xpath": get_xpath(n),
            "text_quote": None
        }
    else:
        record["fields"]["logo"] = {"value": None, "normalized": None}
        # No provenance entry when logo is absent

    # ── 5. location (array — jobs can list multiple locations) ────────────────
    loc_nodes = row.xpath('.//div[contains(@class,"location")] | .//span[contains(@class,"location")]')
    # Filter out salary-tooltip nodes (RemoteOK reuses div.location for the
    # "💰 Upgrade to Premium to see salary" badge when no real location exists)
    SALARY_TOOLTIP = "Upgrade to Premium"
    real_locs = [
        n for n in loc_nodes
        if n.text_content().strip() and SALARY_TOOLTIP not in n.text_content()
    ]
    if real_locs:
        locs = [n.text_content().strip() for n in real_locs]
        # Provenance: point to td.company (parent container of all location divs)
        td_company = row.xpath('.//td[contains(@class,"company")]')
        prov_n = td_company[0] if td_company else real_locs[0]
        record["fields"]["location"] = {"value": locs, "normalized": locs}
        record["provenance"]["location"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(prov_n),
            "xpath": get_xpath(prov_n),
            "text_quote": locs[0]
        }
    else:
        record["fields"]["location"] = {"value": [], "normalized": []}
        # No provenance entry when location is absent

    # ── 6. apply_url ──────────────────────────────────────────────────────────
    apply_nodes = row.xpath('.//td[contains(@class,"source")]//a[contains(@href,"/l/")]')
    if apply_nodes:
        n = apply_nodes[0]
        raw_href = n.get('href', '')
        apply_val = BASE_URL + raw_href if raw_href.startswith('/') else raw_href
        record["fields"]["apply_url"] = {"value": apply_val, "normalized": apply_val}
        record["provenance"]["apply_url"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(n),
            "xpath": get_xpath(n),
            "text_quote": None
        }
    else:
        record["fields"]["apply_url"] = {"value": None, "normalized": None}
        # No provenance entry when apply_url is absent

    # ── 7. tags ───────────────────────────────────────────────────────────────
    tag_nodes = row.xpath('.//td[contains(@class,"tags")]//a[contains(@class,"tag") or contains(@class,"action-add-tag")]')
    if tag_nodes:
        tags = [t.text_content().strip() for t in tag_nodes if t.text_content().strip()]
        # Provenance points to the td.tags container
        td_tags = row.xpath('.//td[contains(@class,"tags")]')
        prov_n = td_tags[0] if td_tags else tag_nodes[0]
        record["fields"]["tags"] = {"value": tags, "normalized": tags}
        record["provenance"]["tags"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(prov_n),
            "xpath": get_xpath(prov_n),
            "text_quote": tags[0] if tags else None
        }
    else:
        record["fields"]["tags"] = {"value": [], "normalized": []}
        # No provenance entry when tags are absent

    # ── 8. salary ─────────────────────────────────────────────────────────────
    salary_nodes = row.xpath('.//div[contains(@class,"salary")]')
    if salary_nodes:
        n = salary_nodes[0]
        val = n.text_content().strip()
        record["fields"]["salary"] = {"value": val, "normalized": val}
        record["provenance"]["salary"] = {
            "snapshot_id": "remoteok_listing",
            "css_selector": get_css(n),
            "xpath": get_xpath(n),
            "text_quote": val
        }
    else:
        record["fields"]["salary"] = {"value": None, "normalized": None}
        # No provenance entry when salary is absent

    records.append(record)

# ── Write output ──────────────────────────────────────────────────────────────
with open('data/gold/by_task/jobs/WBV1_JOBS_REMOTEOK_001_LISTING.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['records'] = records
data['annotation_metadata']['total_records_extracted'] = len(records)

with open('data/gold/by_task/jobs/WBV1_JOBS_REMOTEOK_001_LISTING.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Wrote {len(records)} records.', file=sys.stderr)

# Quick sanity check on first record
r = records[0]
for k, v in r['fields'].items():
    val_str = str(v['value'])[:70] if v['value'] is not None else 'null'
    print(f'  {k}: {val_str}', file=sys.stderr)
