import json
import sys
import re
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

BASE_URL = 'https://www.timeshighereducation.com'

with open('data/raw_snapshots/jobs/timeshighered_listing/page.html', 'rb') as f:
    parser = html.HTMLParser(encoding='utf-8')
    tree = html.fromstring(f.read(), parser=parser)

records = []
items = tree.xpath('//li[contains(@class, "lister__item")]')

valid_idx = 1
for item in items:
    title_node = item.xpath('.//h3[contains(@class, "lister__header")]/a')
    if not title_node:
        continue
    title_node = title_node[0]
    title = title_node.text_content().strip()
    
    href = title_node.get('href', '').strip()
    job_url = BASE_URL + href if href.startswith('/') else href

    record = {
        "gold_record_id": f"WBV1_JOBS_THTJOBS_001_LISTING_{valid_idx:03d}",
        "fields": {},
        "provenance": {}
    }

    def set_field(key, val, node, normalized_val=None):
        if normalized_val is None:
            normalized_val = val
        record["fields"][key] = {"value": val, "normalized": normalized_val}
        if val is None or val == [] or val == {}:
            pass
        else:
            if isinstance(val, str):
                text_quote = val
            elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
                text_quote = val[0]
            else:
                text_quote = None
            record["provenance"][key] = {
                "snapshot_id": "timeshighered_listing",
                "css_selector": get_css(node) if node is not None else None,
                "xpath": get_xpath(node) if node is not None else None,
                "text_quote": text_quote[:50] if text_quote else None
            }

    set_field("job_title", title, title_node)
    set_field("job_url", job_url, title_node)

    logo_node = item.xpath('.//img[contains(@class, "lister__logo")]')
    if logo_node:
        n = logo_node[0]
        logo_url = n.get('src') or n.get('data-src')
        if logo_url and logo_url.startswith('/'):
            logo_url = BASE_URL + logo_url
        set_field("logo", logo_url, n)
    else:
        set_field("logo", None, None)

    desc_node = item.xpath('.//p[contains(@class, "lister__description")]')
    if desc_node:
        d_text = desc_node[0].text_content().strip()
        set_field("description", d_text, desc_node[0])
    else:
        set_field("description", None, None)

    loc_nodes = item.xpath('.//li[contains(@class, "lister__meta-item--location")]')
    if loc_nodes:
        val = loc_nodes[0].text_content().strip()
        set_field("location", val, loc_nodes[0])
    else:
        set_field("location", None, None)

    sal_nodes = item.xpath('.//li[contains(@class, "lister__meta-item--salary")]')
    if sal_nodes:
        set_field("salary", sal_nodes[0].text_content().strip(), sal_nodes[0])
    else:
        set_field("salary", None, None)

    comp_nodes = item.xpath('.//li[contains(@class, "lister__meta-item--recruiter")]')
    if comp_nodes:
        set_field("company", comp_nodes[0].text_content().strip(), comp_nodes[0])
    else:
        set_field("company", None, None)

    records.append(record)
    valid_idx += 1

print(f"Found {len(records)} valid job rows")

with open('data/gold/by_task/jobs/WBV1_JOBS_THTJOBS_001_LISTING.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data["records"] = records
data["annotation_metadata"]["total_records_extracted"] = len(records)

with open('data/gold/by_task/jobs/WBV1_JOBS_THTJOBS_001_LISTING.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

if records:
    print("\nSample fields for first record:")
    for k, v in records[0]["fields"].items():
        print(f"  {k}: {str(v['value'])[:50]}")
