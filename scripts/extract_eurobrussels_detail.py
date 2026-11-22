import json
import re
from bs4 import BeautifulSoup
import os

def get_xpath(element):
    if not element:
        return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name is None:
            break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            idx = 1
            for sib in siblings:
                if sib == child:
                    break
                idx += 1
            components.append(f'{child.name}[{idx}]')
        child = parent
    components.reverse()
    return '/' + '/'.join(components)

def get_css(element):
    if not element or not element.name:
        return None
    def selector_for(el):
        classes = el.get('class', [])
        if classes:
            return f"{el.name}.{'.'.join(classes)}"
        return el.name

    parts = [selector_for(element)]
    for parent in element.parents:
        if parent.name is None or parent.name in ('body', 'html', '[document]'):
            break
        parent_classes = parent.get('class', [])
        if parent_classes:
            parts.append(selector_for(parent))
            break
        parts.append(selector_for(parent))
    parts.reverse()
    return ' > '.join(parts)

def extract_detail():
    html_path = r'data/raw_snapshots/jobs/eurobrussels_detail/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_EUROBRUSSELS_002_DETAIL.json'
    snapshot_id = "eurobrussels_detail"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    # Extract fields
    job_title_el = soup.find('h1')
    job_title = job_title_el.text.strip() if job_title_el else None
    
    job_display = soup.find('div', class_='jobDisplay')
    h2s = [h2 for h2 in job_display.find_all('h2') if h2.text.strip()] if job_display else []
    
    company_el = h2s[1] if len(h2s) > 1 else None
    company_name = company_el.text.strip() if company_el else None
    
    location_el = h2s[2] if len(h2s) > 2 else None
    location = location_el.text.strip() if location_el else None
    
    # Description
    description_el = job_display
    description_val = job_display.text.strip() if job_display else None
    
    # Custom Sections
    sections = {
        'about': {'text': [], 'els': []},
        'job_opp': {'text': [], 'els': []},
        'what_work': {'text': [], 'els': []},
        'skills': {'text': [], 'els': []},
        'offer': {'text': [], 'els': []},
        'app_proc': {'text': [], 'els': []}
    }
    current_section = None
    
    if job_display:
        for child in job_display.children:
            if child.name in ['h3', 'h4']:
                text = child.text.strip().lower()
                if 'about' in text: current_section = 'about'
                elif 'opportunity' in text: current_section = 'job_opp'
                elif 'breakdown' in text or 'key aspects' in text: current_section = 'what_work'
                elif 'profile' in text: current_section = 'skills'
                elif 'offer' in text: current_section = 'offer'
                elif 'procedure' in text: current_section = 'app_proc'
                else: current_section = None
            elif child.name == 'p':
                if current_section in sections:
                    sections[current_section]['text'].append(child.text.strip())
                    sections[current_section]['els'].append(child)
            elif child.name == 'ul':
                if current_section in sections:
                    for li in child.find_all('li'):
                        sections[current_section]['text'].append(li.text.strip())
                    sections[current_section]['els'].append(child)

    # Deadline
    deadline_val = None
    deadline_norm = None
    deadline_el = None
    if job_display:
        for p in job_display.find_all('p'):
            if 'deadline' in p.text.lower():
                m = re.search(r'(\d{1,2}\s+of\s+[A-Za-z]+\s+\d{4})', p.text)
                if m:
                    deadline_val = m.group(1)
                    deadline_el = p
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(deadline_val.replace(' of ', ' '), "%d %B %Y")
                        deadline_norm = dt.strftime("%Y-%m-%d")
                    except Exception:
                        deadline_norm = deadline_val
                break

    # Job URL
    job_url_el = soup.find('link', rel='canonical')
    job_url = job_url_el['href'] if job_url_el else "https://www.eurobrussels.com/job_display/291628/Senior_Communications_Officer_REScoopeu_Brussels_Belgium"

    # Apply Link
    btn = soup.find('button', class_='callToAction')
    apply_link = btn['data-job-url'] if btn and btn.has_attr('data-job-url') else None
    apply_link_el = btn
    
    fields_dict = {
        "job_title": {"value": job_title, "normalized": job_title},
        "job_url": {"value": job_url, "normalized": job_url},
        "company_name": {"value": company_name, "normalized": company_name},
        "location": {"value": location, "normalized": location},
        "description": {"value": description_val[:500] + "..." if description_val else None, "normalized": description_val[:500] + "..." if description_val else None},
        "deadline": {"value": deadline_val, "normalized": deadline_norm},
        "salary": {"value": None, "normalized": None},
        "tags": {"value": None, "normalized": None},
        "about_company": {"value": "\n".join(sections['about']['text']) if sections['about']['text'] else None, "normalized": "\n".join(sections['about']['text']) if sections['about']['text'] else None},
        "role_overview": {"value": "\n".join(sections['job_opp']['text']) if sections['job_opp']['text'] else None, "normalized": "\n".join(sections['job_opp']['text']) if sections['job_opp']['text'] else None},
        "responsibilities": {"value": sections['what_work']['text'] if sections['what_work']['text'] else None, "normalized": sections['what_work']['text'] if sections['what_work']['text'] else None},
        "requirements": {"value": sections['skills']['text'] if sections['skills']['text'] else None, "normalized": sections['skills']['text'] if sections['skills']['text'] else None},
        "benefits": {"value": sections['offer']['text'] if sections['offer']['text'] else None, "normalized": sections['offer']['text'] if sections['offer']['text'] else None},
        "application_procedure": {"value": "\n".join(sections['app_proc']['text']) if sections['app_proc']['text'] else None, "normalized": "\n".join(sections['app_proc']['text']) if sections['app_proc']['text'] else None},
        "apply_link": {"value": apply_link, "normalized": apply_link}
    }
    
    elements_map = {
        "job_title": job_title_el,
        "job_url": job_url_el,
        "company_name": company_el,
        "location": location_el,
        "description": description_el,
        "deadline": deadline_el,
        "about_company": sections['about']['els'][0] if sections['about']['els'] else None,
        "role_overview": sections['job_opp']['els'][0] if sections['job_opp']['els'] else None,
        "responsibilities": sections['what_work']['els'][0] if sections['what_work']['els'] else None,
        "requirements": sections['skills']['els'][0] if sections['skills']['els'] else None,
        "benefits": sections['offer']['els'][0] if sections['offer']['els'] else None,
        "application_procedure": sections['app_proc']['els'][0] if sections['app_proc']['els'] else None,
        "apply_link": apply_link_el
    }
    
    provenance_dict = {}
    for k, v in fields_dict.items():
        if v["value"] is not None:
            el = elements_map.get(k)
            provenance_dict[k] = {
                "snapshot_id": snapshot_id,
                "xpath": get_xpath(el),
                "css_selector": get_css(el),
                "text_quote": ", ".join(v["value"]) if isinstance(v["value"], list) else str(v["value"])[:1000] # truncating large texts
            }
            
    record = {
        "gold_record_id": "WBV1_JOBS_EUROBRUSSELS_002_DETAIL_001",
        "fields": fields_dict,
        "provenance": provenance_dict
    }
    
    data = {
        "annotation_metadata": {
            "total_records_extracted": 1,
            "domain": "jobs",
            "task_type": "detail",
            "website": "eurobrussels"
        },
        "records": [record]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved detail record to {json_path}")

if __name__ == '__main__':
    extract_detail()
