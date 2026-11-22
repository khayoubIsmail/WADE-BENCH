import json
import re
from bs4 import BeautifulSoup

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
    """Build a specific CSS selector by walking up ancestors until a class-bearing element is found."""
    if not element or not element.name:
        return None

    def selector_for(el):
        classes = el.get('class', [])
        if classes:
            return f"{el.name}.{'.'.join(classes)}"
        return el.name

    # Build a path from the element up to the nearest ancestor with a class
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

def extract_jobs():
    html_path = r'data/raw_snapshots/jobs/eurobrussels_listing/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_EUROBRUSSELS_001_LISTING.json'
    snapshot_id = "eurobrussels_listing"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    container = soup.find('div', class_='col-xl-8 col-12')
    ul = container.find('ul')
    lis = ul.find_all('li', recursive=False)
    
    job_items = []
    for li in lis:
        if li.find('h3') and li.find('h3').find('a'):
            job_items.append(li)
            
    print(f"Found {len(job_items)} job items.")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    records = []
    for i, item in enumerate(job_items[:19]):
        a_tag = item.find('h3').find('a')
        job_title = a_tag.text.strip()
        job_url = "https://www.eurobrussels.com" + a_tag['href']
        
        company_div = item.find('div', class_='companyName')
        company_name = company_div.text.strip() if company_div else None
        
        location_div = item.find('div', class_='location')
        location = location_div.text.strip() if location_div else None
        
        desc_p = item.find('p')
        description = desc_p.text.strip() if desc_p else None
        
        img_tag = item.find('img')
        company_logo = img_tag['src'] if img_tag and img_tag.has_attr('src') else None
        
        tag_spans = item.find_all('span', class_='bg-job-tag')
        tags = [span.text.strip() for span in tag_spans]
        tag_element = tag_spans[0] if tag_spans else None
        
        posted_div = item.find('div', class_='postedDate')
        deadline_val = None
        deadline_norm = None
        if posted_div:
            text = posted_div.text
            match = re.search(r'Deadline\s+(.*)', text, re.IGNORECASE)
            if match:
                deadline_val = match.group(1).strip()
                try:
                    from datetime import datetime
                    date_str = deadline_val
                    if not re.search(r'\d{4}', date_str):
                        date_str += " 2026"
                    dt = datetime.strptime(date_str, "%d %B %Y")
                    deadline_norm = dt.strftime("%Y-%m-%d")
                except Exception:
                    deadline_norm = deadline_val
                
        salary_div = item.find('div', class_='salary')
        salary_val = salary_div.text.strip() if salary_div else None
        salary_norm = salary_val
        if salary_val:
            s_clean = salary_val.replace(" ", "")
            m = re.search(r'[\d,\.]+', s_clean)
            if m:
                salary_norm = m.group(0).strip(".,")
                if '.' in salary_norm and ',' in salary_norm:
                    if salary_norm.rindex(',') > salary_norm.rindex('.'):
                        salary_norm = salary_norm.replace('.', '').replace(',', '.')
                    else:
                        salary_norm = salary_norm.replace(',', '')
                elif ',' in salary_norm:
                    parts = salary_norm.split(',')
                    if len(parts[-1]) == 3:
                        salary_norm = salary_norm.replace(',', '')
                    else:
                        salary_norm = salary_norm.replace(',', '.')
        
        fields_dict = {
            "job_title": {"value": job_title, "normalized": job_title},
            "job_url": {"value": job_url, "normalized": job_url},
            "company_name": {"value": company_name, "normalized": company_name},
            "company_logo": {"value": company_logo, "normalized": company_logo},
            "location": {"value": location, "normalized": location},
            "description": {"value": description, "normalized": description},
            "deadline": {"value": deadline_val, "normalized": deadline_norm},
            "salary": {"value": salary_val, "normalized": salary_norm},
            "tags": {"value": tags if tags else None, "normalized": tags if tags else None}
        }
        
        # Build provenance mapping
        elements_map = {
            "job_title": a_tag,
            "job_url": a_tag,
            "company_name": company_div,
            "company_logo": img_tag,
            "location": location_div,
            "description": desc_p,
            "deadline": posted_div,
            "salary": salary_div,
            "tags": tag_element
        }
        
        provenance_dict = {}
        for k, v in fields_dict.items():
            if v["value"] is not None:
                el = elements_map.get(k)
                provenance_dict[k] = {
                    "snapshot_id": snapshot_id,
                    "xpath": get_xpath(el),
                    "css_selector": get_css(el),
                    "text_quote": ", ".join(v["value"]) if isinstance(v["value"], list) else str(v["value"])
                }
        
        record = {
            "gold_record_id": f"WBV1_JOBS_EUROBRUSSELS_001_LISTING_{i+1:03d}",
            "fields": fields_dict,
            "provenance": provenance_dict
        }
        records.append(record)
        
    data['records'] = records
    data['annotation_metadata']['total_records_extracted'] = len(records)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(records)} records to {json_path}.")

if __name__ == '__main__':
    extract_jobs()
