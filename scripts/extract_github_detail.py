import json
import re
from bs4 import BeautifulSoup
from lxml import html as lxml_html

def get_xpath(element):
    """Generate a reliable XPath for a BeautifulSoup element."""
    if element is None:
        return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            index = next((i for i, s in enumerate(siblings) if s is child), 0) + 1
            components.append(f'{child.name}[{index}]')
        child = parent
    components.reverse()
    return '/' + '/'.join(components)

def get_css(element):
    """Generate a reliable CSS selector for a BeautifulSoup element."""
    if element is None:
        return None
    
    # If the element has an ID, use it directly
    if element.get('id'):
        return f"#{element.get('id')}"
        
    components = []
    child = element if element.name else element.parent
    
    for parent in child.parents:
        if parent.name == '[document]':
            break
            
        # Try to use id if parent has it
        if parent.get('id'):
            siblings = parent.find_all(child.name, recursive=False)
            if len(siblings) == 1:
                components.append(child.name)
            else:
                index = next((i for i, s in enumerate(siblings) if s is child), 0) + 1
                components.append(f'{child.name}:nth-of-type({index})')
            components.append(f"#{parent.get('id')}")
            break
            
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            index = next((i for i, s in enumerate(siblings) if s is child), 0) + 1
            components.append(f'{child.name}:nth-of-type({index})')
        child = parent
        
    components.reverse()
    return ' > '.join(components)

def extract_detail():
    html_path = r'data/raw_snapshots/jobs/github_careers_detail/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_GITHUB_002_DETAIL.json'
    snapshot_id = "github_careers_software_engineer_iii_detail"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_str = f.read()
    
    soup = BeautifulSoup(html_str, 'html.parser')
    
    # Extract config
    config = None
    config_script = None
    for script in soup.find_all('script'):
        if script.string and 'window.jobDescriptionConfig' in script.string:
            match = re.search(r'window\.jobDescriptionConfig\s*=\s*(\{.*?\});', script.string, re.DOTALL)
            if match:
                config = json.loads(match.group(1))
                config_script = script
                break
                
    if not config:
        print("Could not find window.jobDescriptionConfig")
        return
        
    job = config.get('job', {})
    
    # We will map fields from job config but we need an element for provenance.
    # We will use the config script element as the source of truth for these structured fields.
    
    # requested fields: title, locations, category, job_type, job_level, remote, req_id, employment_type, applied_url
    
    # title
    title_val = job.get('title')
    title_el = soup.find('h1')
    
    # locations
    locations_val = config.get('jobFormatted', {}).get('locations') or job.get('full_location')
    locations_el = config_script
    
    # category
    category_val = job.get('category', [None])[0] if job.get('category') else None
    if category_val:
        category_val = category_val.strip()
    category_el = config_script
    
    # job_type (Experienced Professional)
    job_type_val = job.get('tags4', [None])[0] if job.get('tags4') else None
    job_type_el = config_script
    
    # job_level (Individual Contributor)
    job_level_val = job.get('tags5', [None])[0] if job.get('tags5') else None
    job_level_el = config_script
    
    # remote (Yes)
    remote_val = job.get('tags6', [None])[0] if job.get('tags6') else None
    remote_el = config_script
    
    # req_id
    req_id_val = job.get('req_id')
    req_id_el = config_script
    
    # employment_type
    employment_type_val = job.get('employment_type')
    employment_type_el = config_script
    
    # applied_url
    applied_url_val = job.get('apply_url')
    applied_url_el = config_script
    
    # --- New section extraction ---
    desc = soup.find('article', id='description-body')
    
    def get_section_text(tag_name, text_match):
        if not desc: return None, None
        heading = desc.find(tag_name, string=lambda s: s and text_match in s)
        if not heading: return None, None
        text_parts = []
        el = heading.next_sibling
        while el:
            if el.name in ['strong', 'p'] and el.text.strip() and el != heading:
                if el.name == 'strong' or el.text.strip() in ['GitHub values', 'Manager fundamentals', 'Leadership principles']:
                    break
            if getattr(el, 'text', None):
                text = el.text.strip()
                if text:
                    text_parts.append(text)
            elif isinstance(el, str) and el.strip():
                text_parts.append(el.strip())
            el = el.next_sibling
        return ' '.join(text_parts), heading

    def get_section_list(tag_name, text_match):
        if not desc: return None, None
        heading = desc.find(tag_name, string=lambda s: s and text_match in s)
        if not heading: return None, None
        ul = heading.find_next_sibling('ul')
        if ul:
            return [li.text.strip() for li in ul.find_all('li')], ul
        return None, None

    about_github, about_el = get_section_text('strong', 'About GitHub')
    overview, overview_el = get_section_text('strong', 'Overview')
    responsibilities, resp_el = get_section_list('strong', 'Responsibilities')
    
    req_p = desc.find('p', string=lambda s: s and 'Required/Minimum Qualifications' in s) if desc else None
    req_ul = req_p.find_next_sibling('ul') if req_p else None
    required_quals = [li.text.strip() for li in req_ul.find_all('li')] if req_ul else []
    
    pref_p = desc.find('p', string=lambda s: s and 'Preferred Qualifications' in s) if desc else None
    pref_ul = pref_p.find_next_sibling('ul') if pref_p else None
    preferred_quals = [li.text.strip() for li in pref_ul.find_all('li')] if pref_ul else []
    
    qualifications = {
        'required_minimum_qualifications': required_quals,
        'preferred_qualifications': preferred_quals
    }
    # For provenance, we'll use the 'Qualifications' heading or the req_p
    qual_el = desc.find('strong', string=lambda s: s and 'Qualifications' in s) if desc else None
    if not qual_el: qual_el = req_p
    
    comp, comp_el = get_section_text('strong', 'Compensation Range')
    values, values_el = get_section_list('p', 'GitHub values')
    mgr, mgr_el = get_section_list('p', 'Manager fundamentals')
    lead, lead_el = get_section_list('p', 'Leadership principles')
    who, who_el = get_section_text('strong', 'Who We Are')
    eeo, eeo_el = get_section_text('strong', 'EEO Statement')

    fields_dict = {
        "title": {"value": title_val, "normalized": title_val},
        "locations": {"value": locations_val, "normalized": locations_val},
        "category": {"value": category_val, "normalized": category_val},
        "job_type": {"value": job_type_val, "normalized": job_type_val},
        "job_level": {"value": job_level_val, "normalized": job_level_val},
        "remote": {"value": remote_val, "normalized": remote_val},
        "req_id": {"value": req_id_val, "normalized": req_id_val},
        "employment_type": {"value": employment_type_val, "normalized": employment_type_val},
        "applied_url": {"value": applied_url_val, "normalized": applied_url_val},
        "about_github": {"value": about_github, "normalized": about_github},
        "overview": {"value": overview, "normalized": overview},
        "responsibilities": {"value": responsibilities, "normalized": responsibilities},
        "qualifications": {"value": qualifications, "normalized": qualifications},
        "compensation_range": {"value": comp, "normalized": comp},
        "github_values": {"value": values, "normalized": values},
        "manager_fundamentals": {"value": mgr, "normalized": mgr},
        "leadership_principles": {"value": lead, "normalized": lead},
        "who_we_are": {"value": who, "normalized": who},
        "eeo_statement": {"value": eeo, "normalized": eeo}
    }
    
    elements_map = {
        "title": title_el,
        "locations": locations_el,
        "category": category_el,
        "job_type": job_type_el,
        "job_level": job_level_el,
        "remote": remote_el,
        "req_id": req_id_el,
        "employment_type": employment_type_el,
        "applied_url": applied_url_el,
        "about_github": about_el,
        "overview": overview_el,
        "responsibilities": resp_el,
        "qualifications": qual_el,
        "compensation_range": comp_el,
        "github_values": values_el,
        "manager_fundamentals": mgr_el,
        "leadership_principles": lead_el,
        "who_we_are": who_el,
        "eeo_statement": eeo_el
    }
    
    provenance_dict = {}
    for k, v in fields_dict.items():
        if v["value"] is not None:
            el = elements_map.get(k)
            if el:
                if el == config_script:
                    provenance_dict[k] = {
                        "snapshot_id": snapshot_id,
                        "xpath": get_xpath(el),
                        "css_selector": "script", # special case for script
                        "text_quote": str(v["value"])[:100] + '...' if len(str(v["value"])) > 100 else str(v["value"])
                    }
                else:
                    text_quote = el.text.strip()
                    if isinstance(v["value"], dict):
                        text_quote = "Qualifications"
                    elif isinstance(v["value"], list) and len(v["value"]) > 0:
                        text_quote = v["value"][0][:100]
                    else:
                        text_quote = text_quote[:100] + '...' if len(text_quote) > 100 else text_quote
                        
                    provenance_dict[k] = {
                        "snapshot_id": snapshot_id,
                        "xpath": get_xpath(el),
                        "css_selector": get_css(el),
                        "text_quote": text_quote
                    }
            else:
                provenance_dict[k] = {
                    "snapshot_id": snapshot_id,
                    "xpath": None,
                    "css_selector": None,
                    "text_quote": None
                }
                
    record = {
        "gold_record_id": "WBV1_JOBS_GITHUB_CAREERS_001_DETAIL_001",
        "fields": fields_dict,
        "provenance": provenance_dict
    }
    
    data = {
        "annotation_metadata": {
            "total_records_extracted": 1,
            "domain": "jobs",
            "task_type": "detail",
            "website": "github_careers",
            "source_snapshot": "page.html",
            "snapshot_id": snapshot_id,
            "human_verified": False,
            "annotator_id": "auto_extracted_review_needed"
        },
        "records": [record]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved detail record to {json_path}")

if __name__ == "__main__":
    extract_detail()
