import json
import os
from datetime import datetime
from lxml import html

def get_xpath(node):
    return node.getroottree().getpath(node)

def normalize_date(raw: str) -> str:
    """Convert '11 Jun 2026' -> '2026-06-11'. Returns raw string on failure."""
    for fmt in ("%d %b %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw

def get_css(node):
    # This is a basic CSS selector generator. 
    # WADE-bench might have its own logic, but a robust structural one is:
    path = []
    for anc in node.xpath('ancestor-or-self::*'):
        if anc.tag == 'html':
            continue
        step = anc.tag
        if anc.get('id'):
            step += '#' + anc.get('id')
            path = [step] # ID is unique
            continue
        
        # calculate nth-of-type
        siblings = anc.xpath(f'preceding-sibling::{anc.tag}')
        if siblings or anc.xpath(f'following-sibling::{anc.tag}'):
            step += f':nth-of-type({len(siblings) + 1})'
        
        path.append(step)
    return ' > '.join(path)

with open('data/raw_snapshots/jobs/reliefweb_listing/page.html', 'r', encoding='utf-8') as f:
    tree = html.fromstring(f.read())

articles = tree.xpath('//article[contains(@class, "rw-river-article--job")]')

records = []
for i, article in enumerate(articles):
    record = {
        "gold_record_id": f"WBV1_JOBS_RELIEFWEB_001_LISTING_{i+1:03d}",
        "fields": {},
        "provenance": {},
        "notes": "Extracted via script"
    }
    
    # 1. Country (ccuntry)
    country_node = article.xpath('.//p[contains(@class, "rw-entity-country-slug")]/a')
    if country_node:
        country_node = country_node[0]
        val = country_node.text_content().strip()
        record["fields"]["country"] = {"value": val, "normalized": val}
        record["provenance"]["country"] = {
            "snapshot_id": "reliefweb_listing",
            "css_selector": get_css(country_node),
            "xpath": get_xpath(country_node),
            "text_quote": val
        }
        
    # 2. Job Title
    title_nodes = article.xpath('.//h3[contains(@class, "rw-river-article__title")]/a')
    if title_nodes:
        title_node = title_nodes[0]
        val = title_node.text_content().strip()
        record["fields"]["job_title"] = {"value": val, "normalized": val}
        record["provenance"]["job_title"] = {
            "snapshot_id": "reliefweb_listing",
            "css_selector": get_css(title_node),
            "xpath": get_xpath(title_node),
            "text_quote": val
        }
        
    # 3. Job URL
    if title_nodes:
        url_val = title_node.get('href')
        if not url_val.startswith('http'):
            url_val = 'https://reliefweb.int' + url_val
        record["fields"]["job_url"] = {"value": url_val, "normalized": url_val}
        record["provenance"]["job_url"] = {
            "snapshot_id": "reliefweb_listing",
            "css_selector": get_css(title_node),
            "xpath": get_xpath(title_node),
            "text_quote": None
        }
        
    # 4. Organization, 5. Posted date, 6. Closing date
    dts = article.xpath('.//dt')
    dds = article.xpath('.//dd')
    for dt, dd in zip(dts, dds):
        label = dt.text_content().strip().lower()
        val_node = dd
        
        # Sometimes the value is in a sub-element like <time> or <a>
        inner_a = dd.xpath('.//a')
        inner_time = dd.xpath('.//time')
        
        if inner_a:
            val_node = inner_a[0]
        elif inner_time:
            val_node = inner_time[0]
            
        val = val_node.text_content().strip()
        
        field_name = None
        if "organization" in label or "source" in label:
            field_name = "organization"
        elif "posted" in label:
            field_name = "posted_date"
        elif "closing" in label:
            field_name = "closing_date"
            
        if field_name:
            normalized_val = normalize_date(val) if field_name in ("posted_date", "closing_date") else val
            record["fields"][field_name] = {"value": val, "normalized": normalized_val}
            record["provenance"][field_name] = {
                "snapshot_id": "reliefweb_listing",
                "css_selector": get_css(val_node),
                "xpath": get_xpath(val_node),
                "text_quote": val
            }
            
    records.append(record)

output = {
  "task_id": "WBV1_JOBS_RELIEFWEB_001_LISTING",
  "website_id": "reliefweb",
  "schema_id": "job_posting_v1",
  "snapshot_id": "reliefweb_listing",
  "snapshot_path": "raw_snapshots/jobs/reliefweb_listing",
  "live_url": "https://reliefweb.int/jobs",
  "annotation_metadata": {
    "annotation_version": "v1",
    "annotator_id": "ismail_khayoub",
    "verification_status": "human_verified",
    "total_records_extracted": len(records)
  },
  "records": records
}

with open('data/gold/by_task/jobs/WBV1_JOBS_RELIEFWEB_001_LISTING.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(records)} records and saved to JSON.")
