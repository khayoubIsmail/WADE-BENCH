import json
import sys
import re
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

with open('data/raw_snapshots/jobs/remoteok_detail/page.html', 'rb') as f:
    tree = html.fromstring(f.read())

record = {
    "gold_record_id": "WBV1_JOBS_REMOTEOK_002_DETAIL_001",
    "fields": {},
    "provenance": {}
}

def set_field(key, val, node, normalized_val=None):
    if normalized_val is None:
        normalized_val = val
    record["fields"][key] = {"value": val, "normalized": normalized_val}
    if val is None or val == [] or val == {}:
        # Omit provenance if empty
        pass
    else:
        if isinstance(val, str):
            text_quote = val
        elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
            text_quote = val[0]
        else:
            text_quote = None
            
        record["provenance"][key] = {
            "snapshot_id": "remoteok_detail",
            "css_selector": get_css(node) if node is not None else None,
            "xpath": get_xpath(node) if node is not None else None,
            "text_quote": text_quote
        }

# We assume the detail snapshot has exactly one job row that is expanded.
# We can find it by looking for the row with class "expand" and "active" or simply the first tr.job
job_tr = tree.xpath('//tr[contains(@class, "job") and contains(@class, "active")]')[0]
job_id = job_tr.get("data-id")
expand_tr = tree.xpath(f'//tr[contains(@class, "expand-{job_id}")]')[0]

# Basic info
title_node = job_tr.xpath('.//h2[@itemprop="title"]')[0]
set_field("job_title", title_node.text_content().strip(), title_node)

company_nodes = job_tr.xpath('.//h3[@itemprop="name"] | .//div[contains(@class,"company")]')
if company_nodes:
    set_field("company", company_nodes[0].text_content().strip(), company_nodes[0])

logo_nodes = job_tr.xpath('.//td[contains(@class,"image")]//img')
if logo_nodes:
    n = logo_nodes[0]
    val = n.get('src') or n.get('data-src')
    set_field("logo", val, n)
else:
    set_field("logo", None, None)

loc_nodes = job_tr.xpath('.//div[contains(@class,"location")]')
real_locs = [n for n in loc_nodes if "Upgrade to Premium" not in n.text_content()]
if real_locs:
    val = [n.text_content().strip() for n in real_locs]
    # To keep provenance text_quote valid, we pick the first
    record["fields"]["location"] = {"value": val, "normalized": val}
    record["provenance"]["location"] = {
        "snapshot_id": "remoteok_detail",
        "css_selector": get_css(real_locs[0]),
        "xpath": get_xpath(real_locs[0]),
        "text_quote": val[0]
    }
else:
    set_field("location", [], None)

tag_nodes = job_tr.xpath('.//td[contains(@class,"tags")]//a[contains(@class,"tag") or contains(@class,"action-add-tag")]')
if tag_nodes:
    val = [t.text_content().strip() for t in tag_nodes if t.text_content().strip()]
    # Remove duplicates preserving order if necessary
    seen = set()
    val_unique = [x for x in val if not (x in seen or seen.add(x))]
    record["fields"]["tags"] = {"value": val_unique, "normalized": val_unique}
    record["provenance"]["tags"] = {
        "snapshot_id": "remoteok_detail",
        "css_selector": get_css(job_tr.xpath('.//td[contains(@class,"tags")]')[0]),
        "xpath": get_xpath(job_tr.xpath('.//td[contains(@class,"tags")]')[0]),
        "text_quote": val_unique[0] if val_unique else None
    }
else:
    set_field("tags", [], None)

apply_nodes = expand_tr.xpath('.//a[contains(@href, "/l/") or contains(@class, "apply")]')
if not apply_nodes:
    apply_nodes = job_tr.xpath('.//a[contains(@href, "/l/") or contains(@class, "apply")]')
    
if apply_nodes:
    href = apply_nodes[0].get('href', '')
    url = BASE_URL + href if href.startswith('/') else href
    set_field("apply_url", url, apply_nodes[0])
else:
    set_field("apply_url", None, None)

# Description fields
desc_nodes = expand_tr.xpath('.//div[@class="html"] | .//div[@itemprop="description"] | .//div[contains(@class, "description")]')
desc = desc_nodes[0] if desc_nodes else None

set_field("Working Hours", None, None)
set_field("Department", None, None)
set_field("Type of Employment", None, None)
set_field("The Ideal Candidate", [], None)
set_field("Key Responsibilities", {}, None)
set_field("Skills, Experience & Attributes", {}, None)
set_field("Deadline", None, None)
set_field("full description", None, None)

if desc is not None:
    # Full description
    full_text = desc.text_content().strip()
    set_field("full description", full_text, desc)
    record["provenance"]["full description"]["text_quote"] = full_text[:50]
    
    current_section = None
    current_subsection = None
    
    ideal_candidate = []
    key_resp = {
        "Business Process Optimization (Lean-Focused)": [],
        "Requirements Gathering & Process Mapping": [],
        "Digital Solutions, Automation & AI": [],
        "Business Applications Support": [],
        "Data, Reporting & Visibility": [],
        "Documentation, SOPs & Learning Systems": [],
        "Governance, Continuity & Good Practice": [],
        "End-User Support & Adoption": [],
        "ICT & Technical Coordination": []
    }
    skills_exp = {
        "Required": [],
        "Preferred": [],
        "What Success Looks Like": []
    }
    
    # Track provenance nodes for the complex objects to point to the container (the description div itself)
    prov_desc = desc
    
    for el in desc.xpath('.//*'):
        if len(el):
            continue # only process leaf nodes to avoid duplicate text
        txt = el.text_content().strip()
        if not txt:
            continue
            
        if el.tag == 'strong':
            if "Working Hours:" in txt:
                val = txt.replace("Working Hours:", "").strip()
                set_field("Working Hours", val, el)
            elif "Department:" in txt:
                val = txt.replace("Department:", "").strip()
                set_field("Department", val, el)
            elif "Type of Employment:" in txt:
                val = txt.replace("Type of Employment:", "").strip()
                set_field("Type of Employment", val, el)
            elif "Location:" in txt:
                val = txt.replace("Location:", "").strip()
                # Wrap in list to match array format
                set_field("location", [val], el)
            elif "Deadline:" in txt:
                val = txt.replace("Deadline:", "").strip()
                norm_val = val
                clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', val)
                try:
                    dt = datetime.strptime(clean_date, "%B %d, %Y")
                    norm_val = dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass
                set_field("Deadline", val, el, normalized_val=norm_val)
            elif txt == "The Ideal Candidate":
                current_section = "The Ideal Candidate"
                current_subsection = None
            elif txt == "Key Responsibilities":
                current_section = "Key Responsibilities"
                current_subsection = None
            elif txt == "Skills, Experience & Attributes":
                current_section = "Skills, Experience & Attributes"
                current_subsection = None
            elif current_section == "Key Responsibilities" and txt in key_resp:
                current_subsection = txt
            elif current_section == "Skills, Experience & Attributes" and txt in skills_exp:
                current_subsection = txt
        elif el.tag in ['p', 'li']:
            # Strip bullet characters
            clean_txt = txt.lstrip('•').strip()
            if not clean_txt:
                continue
                
            if current_section == "The Ideal Candidate":
                ideal_candidate.append(clean_txt)
            elif current_section == "Key Responsibilities" and current_subsection:
                key_resp[current_subsection].append(clean_txt)
            elif current_section == "Skills, Experience & Attributes" and current_subsection:
                skills_exp[current_subsection].append(clean_txt)

    if ideal_candidate:
        joined_candidate = " ".join(ideal_candidate)
        set_field("The Ideal Candidate", joined_candidate, prov_desc)
        record["provenance"]["The Ideal Candidate"]["text_quote"] = joined_candidate[:50]
        
    if any(key_resp.values()):
        set_field("Key Responsibilities", {k: v for k, v in key_resp.items() if v}, prov_desc)
        first_key = next((k for k, v in key_resp.items() if v), None)
        record["provenance"]["Key Responsibilities"]["text_quote"] = key_resp[first_key][0] if first_key else None
        
    if any(skills_exp.values()):
        set_field("Skills, Experience & Attributes", {k: v for k, v in skills_exp.items() if v}, prov_desc)
        first_key = next((k for k, v in skills_exp.items() if v), None)
        record["provenance"]["Skills, Experience & Attributes"]["text_quote"] = skills_exp[first_key][0] if first_key else None


# Output
with open('data/gold/by_task/jobs/WBV1_JOBS_REMOTEOK_002_DETAIL.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Need to preserve job_url as per schema
if "job_url" in data["records"][0]["fields"]:
    job_url_val = data["records"][0]["fields"]["job_url"]["value"]
    set_field("job_url", job_url_val, tree.xpath('//h1')[0]) # dummy provenance

data["records"] = [record]
data["annotation_metadata"]["total_records_extracted"] = 1

with open('data/gold/by_task/jobs/WBV1_JOBS_REMOTEOK_002_DETAIL.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Extraction complete.", file=sys.stderr)
for k, v in record["fields"].items():
    val = v["value"]
    if isinstance(val, dict):
        print(f"  {k}: [dict with {len(val)} keys]", file=sys.stderr)
    elif isinstance(val, list):
        print(f"  {k}: [list with {len(val)} items]", file=sys.stderr)
    else:
        print(f"  {k}: {str(val)[:50]}", file=sys.stderr)
