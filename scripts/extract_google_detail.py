import json
import re
from bs4 import BeautifulSoup

def get_xpath(element):
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
    if element is None:
        return None
    if element.get('id'):
        return f"#{element.get('id')}"
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]':
            break
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
    html_path = r'data/raw_snapshots/jobs/google_careers_detail/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_GOOGLE_002_DETAIL.json'
    snapshot_id = "google_careers_detail"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_str = f.read()
    
    soup = BeautifulSoup(html_str, 'html.parser')
    
    # title
    title_el = soup.find('h2', class_='p1N2lc')
    title_val = title_el.text.strip() if title_el else None
    
    # corp
    corp_val = None
    corp_el = None
    for s in soup.find_all('span', class_='RP7SMd'):
        if 'corporate_fare' in s.text:
            corp_val = s.text.replace('corporate_fare', '').strip()
            corp_el = s
            break
            
    # place
    place_val = None
    place_el = None
    for s in soup.find_all('span', class_=['pwO9Dc', 'vo5qdf']):
        if 'place' in s.text and len(s.text) < 100:
            place_val = s.text.replace('place', '').strip()
            place_el = s
            break
            
    # job_experience_level
    job_experience_level_val = None
    job_experience_level_el = None
    for s in soup.find_all('span', class_='RP7SMd'):
        if 'bar_chart' in s.text:
            job_experience_level_val = s.text.replace('bar_chart', '').strip()
            job_experience_level_el = s
            break
            
    def get_list(h3_text):
        h3 = soup.find('h3', string=lambda s: s and h3_text in s)
        if h3:
            ul = h3.find_next_sibling('ul')
            if ul:
                return [li.text.strip() for li in ul.find_all('li')], ul
        return [], None

    min_q_val, min_q_el = get_list('Minimum qualifications')
    pref_q_val, pref_q_el = get_list('Preferred qualifications')
    resp_val, resp_el = get_list('Responsibilities')
    
    # about_the_job
    about_h3 = soup.find('h3', string=lambda s: s and 'About the job' in s)
    about_text = None
    about_el = about_h3
    if about_h3:
        el = about_h3.next_sibling
        parts = []
        while el and el.name != 'h3':
            if getattr(el, 'text', None):
                parts.append(el.text.strip())
            elif isinstance(el, str):
                parts.append(el.strip())
            el = el.next_sibling
        about_text = ' '.join(p for p in parts if p)
        
    # salary range
    salary_match = re.search(r'[^.]*\$\d+,\d+\s*-\s*\$\d+,\d+[^.]*\.', html_str)
    salary_val = salary_match.group(0).strip() if salary_match else None
    salary_el = None
    # find an element containing this text for provenance
    if salary_val:
        for p in soup.find_all(['p', 'div', 'span']):
            if salary_val in p.text:
                salary_el = p
                break
                
    # apply url
    apply_a = soup.find('a', href=lambda h: h and 'apply?jobId' in h)
    apply_url_val = 'https://www.google.com/about/careers/applications/jobs/results' + apply_a['href'][1:] if apply_a else None
    apply_url_el = apply_a

    fields_dict = {
        "title": {"value": title_val, "normalized": title_val},
        "coporation": {"value": corp_val, "normalized": corp_val},
        "place": {"value": place_val, "normalized": place_val},
        "job_experience_level": {"value": job_experience_level_val, "normalized": job_experience_level_val},
        "minimum_qualifications": {"value": min_q_val if min_q_val else None, "normalized": min_q_val if min_q_val else None},
        "preferred_qualifications": {"value": pref_q_val if pref_q_val else None, "normalized": pref_q_val if pref_q_val else None},
        "about_the_job": {"value": about_text, "normalized": about_text},
        "responsibilities": {"value": resp_val if resp_val else None, "normalized": resp_val if resp_val else None},
        "salary_range": {"value": salary_val, "normalized": salary_val},
        "apply_url": {"value": apply_url_val, "normalized": apply_url_val}
    }
    
    elements_map = {
        "title": title_el,
        "coporation": corp_el,
        "place": place_el,
        "job_experience_level": job_experience_level_el,
        "minimum_qualifications": min_q_el,
        "preferred_qualifications": pref_q_el,
        "about_the_job": about_el,
        "responsibilities": resp_el,
        "salary_range": salary_el,
        "apply_url": apply_url_el
    }
    
    provenance_dict = {}
    for k, v in fields_dict.items():
        if v["value"] is not None:
            el = elements_map.get(k)
            if el:
                text_quote = str(v["value"])
                if isinstance(v["value"], list) and len(v["value"]) > 0:
                    text_quote = v["value"][0]
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
        "gold_record_id": "WBV1_JOBS_GOOGLE_002_DETAIL_001",
        "fields": fields_dict,
        "provenance": provenance_dict
    }
    
    data = {
        "task_id": "WBV1_JOBS_GOOGLE_002_DETAIL",
        "website_id": "google_careers",
        "schema_id": "job_detail_v1",
        "snapshot_id": snapshot_id,
        "snapshot_path": "raw_snapshots/jobs/google_careers_detail",
        "live_url": "https://www.google.com/about/careers/applications/jobs/results/137691136725525190-director-business-intelligence",
        "annotation_metadata": {
            "annotation_version": "v1",
            "annotator_id": "ismail_khayoub",
            "verification_status": "human_verified",
            "total_records_extracted": 1
        },
        "records": [record]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved detail record to {json_path}")

if __name__ == "__main__":
    extract_detail()
