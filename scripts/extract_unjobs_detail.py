import json
import sys
import re
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

with open('data/raw_snapshots/jobs/unjobs_detail/page.html', 'rb') as f:
    parser = html.HTMLParser(encoding='utf-8')
    tree = html.fromstring(f.read(), parser=parser)

record = {
    "gold_record_id": "WBV1_JOBS_UNJOBS_002_DETAIL_001",
    "fields": {},
    "provenance": {}
}

def set_field(key, val, node, normalized_val=None, text_quote=None, css=None, xpath=None):
    if val is None or val == [] or val == {} or val == "":
        return
    if normalized_val is None:
        normalized_val = val
        
    record["fields"][key] = {"value": val, "normalized": normalized_val}
    
    if text_quote is None:
        if isinstance(val, str):
            text_quote = val[:50]
        elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
            text_quote = val[0][:50]
            
    if not css and node is not None:
        css = get_css(node)
    if not xpath and node is not None:
        xpath = get_xpath(node)
        
    if css or xpath:
        record["provenance"][key] = {
            "snapshot_id": "unjobs_detail",
            "css_selector": css or "",
            "xpath": xpath or "",
            "text_quote": text_quote
        }

# Basic Fields
title_nodes = tree.xpath('//title')
if title_nodes:
    title_text = title_nodes[0].text_content().strip()
    if ' | ' in title_text:
        title_text = title_text.split(' | ')[0]
    if title_text.startswith('UNU Vacancy: '):
        title_text = title_text.replace('UNU Vacancy: ', '')
    set_field("job_title", title_text, title_nodes[0])

og_url = tree.xpath('//meta[@property="og:url"]')
if og_url:
    set_field("job_url", og_url[0].get('content'), og_url[0])

org_a = tree.xpath('//a[contains(@href, "/organizations/")]')
if org_a:
    set_field("company", org_a[0].text_content().strip(), org_a[0])

city_li = tree.xpath('//li[contains(text(), "City:")]//a')
country_li = tree.xpath('//li[contains(text(), "Country:")]//a')
location_parts = []
loc_node = None
if city_li:
    location_parts.append(city_li[0].text_content().strip())
    loc_node = city_li[0]
if country_li:
    location_parts.append(country_li[0].text_content().strip())
    if loc_node is None:
        loc_node = country_li[0]
if location_parts:
    set_field("location", ", ".join(location_parts), loc_node)

# Job description
desc_div = tree.xpath('//div[contains(@class, "fp-snippet")]')
desc_node = desc_div[0] if desc_div else None
if desc_div:
    desc_text = desc_div[0].text_content().strip()
    desc_text = re.sub(r'\s{3,}', '\n\n', desc_text)
    set_field("job_description", desc_text, desc_div[0])

    # Dynamic Parsing
    
    # Responsibilities
    resp_section = re.search(r'Responsibilities(.*?)(?:Key performance indicators|Competencies)', desc_text, re.DOTALL)
    if resp_section:
        r_text = resp_section.group(1)
        resps = re.findall(r'\d\.\s*([A-Za-z].*?)(?:\s{2,}|\n)', r_text)
        resps = [r.replace('Dictionaries & Encyclopedias', '').strip() for r in resps]
        norm_resps = [
            "SDG University Platform coordination",
            "Outreach and communication support",
            "HESI coordination",
            "Inter-network taskforce and knowledge sharing",
            "Other assigned duties"
        ]
        set_field("responsibilities", resps, desc_node, normalized_val=norm_resps)
    
    # Qualifications
    qual_section = re.search(r'Qualifications.*?1\)\s*(Education and certification).*?2\)\s*(Experience).*?(Language Requirements)', desc_text, re.IGNORECASE | re.DOTALL)
    if qual_section:
        quals = [qual_section.group(1).strip(), qual_section.group(2).strip(), qual_section.group(3).strip()]
        # "Language Requirements" -> "Language requirements"
        quals[2] = quals[2].capitalize().replace(' requirements', ' requirements')
        norm_quals = ["education", "experience", "language_requirements"]
        set_field("qualifications", quals, desc_node, normalized_val=norm_quals)
    
    # Duration
    dur = re.search(r'Duration\s+(.*?)\s+Remuneration', desc_text, re.IGNORECASE | re.DOTALL)
    if dur:
        set_field("duration", dur.group(1).strip(), desc_node, 
                  normalized_val={"start": "2026-06", "end": "2027-03-31", "tentative": True})
              
    # Remuneration
    rem = re.search(r'Remuneration\s+.*?(Daily Fee:.*?)(?=\s+Payment schedule)', desc_text, re.IGNORECASE | re.DOTALL)
    if rem:
        rem_text = re.sub(r'console\.log.*?;\s*', '', rem.group(1))
        rem_text = re.sub(r'\n+', '; ', rem_text.strip())
        set_field("remuneration", rem_text, desc_node,
                  normalized_val={"currency": "JPY", "daily_fee": 23700, "maximum_total": 4740000, "maximum_days": 200})
              
    # Expected Start Date
    start = re.search(r'Expected start date\s+(.*?)\s+How to Apply', desc_text, re.IGNORECASE | re.DOTALL)
    if start:
        set_field("expected_start_date", start.group(1).strip(), desc_node, normalized_val="as_soon_as_possible")
    
    # Application Deadline
    dead = re.search(r'Application Deadline\s+(.*?)\s+Assessment', desc_text, re.IGNORECASE | re.DOTALL)
    if dead:
        set_field("application_deadline", dead.group(1).strip(), desc_node, normalized_val="2026-06-02T23:59:00+09:00")
    
    # Special Notice block (contains Visa, Employment status)
    spec = re.search(r'Special notice\s+(UNU does not sponsor a working visa for this position\.)\s+(Consultants do not hold international civil servant status nor are they considered a "staff member" as defined in the United Nations Staff Rules and Regulations\.)', desc_text, re.IGNORECASE | re.DOTALL)
    if spec:
        visa_text = spec.group(1).strip()
        emp_text = spec.group(2).strip()
        # The user JSON had a slightly modified emp text, we'll extract verbatim from HTML but normalize as requested
        set_field("visa_sponsorship", visa_text, desc_node, normalized_val=False)
        set_field("employment_status", emp_text.replace('"', ''), desc_node, normalized_val="consultant_not_staff_member")

    # Extra fields added per user request
    # Competencies
    comp = re.search(r'Competencies.*?\n(.*?)Qualifications', desc_text, re.IGNORECASE | re.DOTALL)
    if comp:
        # Strip internal noise like "Communications & Media Studies" which often leaks from sidebars
        c_text = comp.group(1).strip()
        c_text = re.sub(r'Communications & Media Studies', '', c_text).strip()
        set_field("competencies", c_text, desc_node)

    # Payment schedule and conditions
    pay = re.search(r'Payment schedule and conditions:\s+(.*?)\s+Expected start date', desc_text, re.IGNORECASE | re.DOTALL)
    if pay:
        p_text = pay.group(1).strip()
        p_text = re.sub(r'Dictionaries & Encyclopedias', '', p_text).strip()
        set_field("payment_schedule_and_conditions", p_text, desc_node)

    # How to Apply
    apply = re.search(r'How to Apply\s+(.*?)\s+Application Deadline', desc_text, re.IGNORECASE | re.DOTALL)
    if apply:
        a_text = apply.group(1).strip()
        a_text = re.sub(r'Communications & Media Studies', '', a_text).strip()
        set_field("how_to_apply", a_text, desc_node)

    # Assessment
    assess = re.search(r'Assessment\s+(.*?)\s+Special notice', desc_text, re.IGNORECASE | re.DOTALL)
    if assess:
        set_field("assessment", assess.group(1).strip(), desc_node)

    # Information about UNU rosters
    rost = re.search(r'Information about UNU rosters\s+(.*?)\s+Scam warning', desc_text, re.IGNORECASE | re.DOTALL)
    if rost:
        set_field("information_about_unu_rosters", rost.group(1).strip(), desc_node)

    # Language Requirements
    lang = re.search(r'Language Requirements.*?\s+(.*?)Duration', desc_text, re.IGNORECASE | re.DOTALL)
    if lang:
        set_field("language_requirements", lang.group(1).strip(), desc_node)

# Skills
skills = tree.xpath('//a[contains(@href, "skill")]')
if skills:
    skill_list = [s.text_content().strip() for s in skills]
    if skill_list:
        set_field("skills", skill_list, skills[0])

# Tags
tags = tree.xpath('//a[contains(@href, "tag")]')
if tags:
    tag_list = [t.text_content().strip() for t in tags]
    if tag_list:
        set_field("tags", tag_list, tags[0])

# Office
office_li = tree.xpath('//li[contains(text(), "Office:")]')
if office_li:
    office_text = office_li[0].text_content().replace('Office:', '').strip()
    set_field("office", office_text, office_li[0])

# About UN University
if desc_div:
    m = re.search(r'About UN University \(UNU\)\s+(.*?)\s+About Office/Institute', desc_text, re.DOTALL)
    if m:
        set_field("about_unu", m.group(1).strip(), desc_node)

# About Office/Institute
if desc_div:
    m = re.search(r'About Office/Institute\s+(.*?)\s+Responsibilities', desc_text, re.DOTALL)
    if m:
        set_field("about_office_institute", m.group(1).strip(), desc_node)

print("Fields extracted:")
for k, v in record["fields"].items():
    val = v['value']
    print(f"  {k}: {repr(str(val)[:70])}")

output_file = 'data/gold/by_task/jobs/WBV1_JOBS_UNJOBS_002_DETAIL.json'

with open(output_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

data["records"] = [record]
data["annotation_metadata"]["total_records_extracted"] = 1

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nExtraction complete. Wrote to {output_file}")
