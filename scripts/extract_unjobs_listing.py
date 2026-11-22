import json
import sys
from lxml import html

sys.stdout.reconfigure(encoding='utf-8')

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

with open('data/raw_snapshots/jobs/unjobs_listing/page.html', 'rb') as f:
    parser = html.HTMLParser(encoding='utf-8')
    tree = html.fromstring(f.read(), parser=parser)

records = []
jobs = tree.xpath('//div[contains(@class, "job")]')
valid_jobs = []
for job in jobs:
    a_title = job.xpath('./a[@class="jtitle"]')
    if a_title:
        valid_jobs.append((job, a_title[0]))

for i, (job, a) in enumerate(valid_jobs):
    record_id = f"WBV1_JOBS_UNJOBS_001_LISTING_{i+1:03d}"
    record = {
        "gold_record_id": record_id,
        "fields": {},
        "provenance": {}
    }

    def set_field(key, val, node, normalized_val=None, tail=False):
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
            
        css_sel = get_css(node)
        # In this dataset, if the text is in the tail, we represent the selector as targeting the element whose tail it is
        record["provenance"][key] = {
            "snapshot_id": "unjobs_listing",
            "css_selector": css_sel,
            "xpath": get_xpath(node) + ("/text()[1]" if tail else ""),
            "text_quote": text_quote
        }

    # Job title
    title_text = a.text_content().strip()
    set_field("job_title", title_text, a)

    # Job URL
    url = a.get('href')
    set_field("job_url", url, a)

    # Company
    brs = job.xpath('./br')
    if brs and brs[0].tail:
        company = brs[0].tail.strip()
        set_field("company", company, brs[0], tail=True)

    # Date publication
    time_nodes = job.xpath('./time')
    if time_nodes:
        time_node = time_nodes[0]
        date_raw = time_node.text_content().strip()
        date_norm = time_node.get('datetime')
        if date_norm:
            # Usually format is 2026-05-28T10:26:28Z, so we take the date part
            date_norm = date_norm.split('T')[0]
        else:
            date_norm = date_raw
        set_field("date_publication", date_raw, time_node, normalized_val=date_norm)

    records.append(record)

print(f"Extracted {len(records)} records.")
for i in range(min(2, len(records))):
    print(f"Record {i+1}:")
    for k, v in records[i]["fields"].items():
        print(f"  {k}: {v['value']}")

output_file = 'data/gold/by_task/jobs/WBV1_JOBS_UNJOBS_001_LISTING.json'

data = {
    "annotation_metadata": {
        "snapshot_id": "unjobs_listing",
        "task_id": "WBV1_JOBS_UNJOBS_001_LISTING",
        "total_records_extracted": len(records)
    },
    "records": records
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\\nWrote output to {output_file}")
