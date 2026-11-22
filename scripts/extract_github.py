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
        # Ignore dynamic angular classes like ng-tns-c77-16
        filtered_classes = [c for c in classes if not c.startswith('ng-')]
        if filtered_classes:
            return f"{el.name}.{'.'.join(filtered_classes)}"
        return el.name

    parts = [selector_for(element)]
    for parent in element.parents:
        if parent.name is None or parent.name in ('body', 'html', '[document]'):
            break
        parent_classes = parent.get('class', [])
        filtered_parent_classes = [c for c in parent_classes if not c.startswith('ng-')]
        if filtered_parent_classes:
            parts.append(selector_for(parent))
            break
        parts.append(selector_for(parent))
    parts.reverse()
    return ' > '.join(parts)

def extract_listings():
    html_path = r'data/raw_snapshots/jobs/github_careers_listing/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_GITHUB_001_LISTING.json'
    snapshot_id = "github_careers_listing"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    panels = soup.find_all('mat-expansion-panel', class_='search-result-item')
    records = []
    
    for i, panel in enumerate(panels):
        # Job Title
        job_title_el = panel.find('p', class_='job-title')
        title_span = job_title_el.find('span', itemprop='title') if job_title_el else None
        job_title = title_span.text.strip() if title_span else (job_title_el.text.strip() if job_title_el else None)
        
        # Req ID
        req_id_el = panel.find('p', class_='req-id')
        req_id_span = req_id_el.find('span') if req_id_el else None
        req_id = req_id_span.text.strip() if req_id_span else None
        
        # Location
        loc_div = panel.find('div', class_=lambda c: c and 'job-result__location' in c)
        loc_span = loc_div.find('span', class_=lambda c: c and 'label-value' in c) if loc_div else None
        location = loc_span.text.strip() if loc_span else None
        location_el = loc_span or loc_div
        
        # Type
        type_span = None
        if loc_div:
            for s in loc_div.find_all('span'):
                if s.text.strip().lower() == 'remote':
                    type_span = s
                    break
        type_val = type_span.text.strip() if type_span else None
        
        # Categories (Tags)
        cat_div = panel.find('div', class_=lambda c: c and 'job-result__categories' in c)
        cat_span = cat_div.find('span', class_=lambda c: c and 'label-value' in c) if cat_div else None
        tags = [cat_span.text.strip()] if cat_span else []
        tags_el = cat_span or cat_div
        
        # Apply URL
        apply_url_el = panel.find(lambda t: t.name == 'a' and 'Apply Now' in t.get_text())
        apply_url = apply_url_el['href'] if apply_url_el and apply_url_el.has_attr('href') else None
        
        fields_dict = {
            "job_title": {"value": job_title, "normalized": job_title},
            "req_id": {"value": req_id, "normalized": req_id},
            "location": {"value": location, "normalized": location},
            "type": {"value": type_val, "normalized": type_val},
            "categories": {"value": tags if tags else None, "normalized": tags if tags else None},
            "apply_url": {"value": apply_url, "normalized": apply_url}
        }
        
        elements_map = {
            "job_title": title_span or job_title_el,
            "req_id": req_id_span or req_id_el,
            "location": location_el,
            "type": type_span,
            "categories": tags_el,
            "apply_url": apply_url_el
        }
        
        provenance_dict = {}
        for k, v in fields_dict.items():
            if v["value"] is not None:
                el = elements_map.get(k)
                if el:
                    provenance_dict[k] = {
                        "snapshot_id": snapshot_id,
                        "xpath": get_xpath(el),
                        "css_selector": get_css(el),
                        "text_quote": ", ".join(v["value"]) if isinstance(v["value"], list) else str(v["value"])
                    }
                else:
                    provenance_dict[k] = {
                        "snapshot_id": snapshot_id,
                        "xpath": None,
                        "css_selector": None,
                        "text_quote": None
                    }
                
        record = {
            "gold_record_id": f"WBV1_JOBS_GITHUB_001_LISTING_{str(i+1).zfill(3)}",
            "fields": fields_dict,
            "provenance": provenance_dict
        }
        records.append(record)
        
    data = {
        "annotation_metadata": {
            "total_records_extracted": len(records),
            "domain": "jobs",
            "task_type": "listing",
            "website": "github"
        },
        "records": records
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(records)} listing records to {json_path}")

if __name__ == '__main__':
    extract_listings()
