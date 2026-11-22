import json
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

def extract_listings():
    html_path = r'data/raw_snapshots/jobs/google_careers_listing/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_GOOGLE_001_LISTING.json'
    snapshot_id = "google_careers_listing"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    items = soup.find_all('li', class_='lLd3Je')
    records = []
    
    for i, item in enumerate(items):
        # title
        title_el = item.find('h3', class_='QJPWVe')
        title_val = title_el.text.strip() if title_el else None
        
        # url_offer
        a_tag = item.find('a', class_='WpHeLc')
        url_val = 'https://www.google.com/about/careers/applications/' + a_tag['href'] if a_tag and a_tag.has_attr('href') else None
        
        # corporate_fare and place
        loc_p = item.find('p', class_='l103df')
        corporate_fare_val = None
        corporate_fare_el = loc_p
        place_val = None
        place_el = loc_p
        
        if loc_p:
            if '|' in loc_p.text:
                corporate_fare_val = loc_p.text.split('|')[0].strip()
            span_loc = loc_p.find('span', class_='r0wTof')
            if span_loc:
                place_val = span_loc.text.strip()
                place_el = span_loc
                
        # badges (job_experience_level, type)
        job_experience_level_val = None
        job_experience_level_el = None
        type_val = None
        type_el = None
        
        badges = item.find_all(['span', 'button'], class_=lambda c: c and ('wVSTAb' in c or 'RP7SMd' in c or 'VfPpkd-LgbsSe' in c))
        
        # Collect all valid badge texts and elements
        extracted_badges = []
        for b in item.find_all(['span', 'div'], recursive=True):
            if 'wVSTAb' in (b.get('class') or []) or 'RP7SMd' in (b.get('class') or []):
                text = b.text.strip().replace('bar_chart', '').replace('corporate_fare', '').replace('laptop_windows', '')
                if text and 'Google' not in text and 'YouTube' not in text:
                    extracted_badges.append((text, b))
                    
        for text, el in extracted_badges:
            if text in ['Early', 'Mid', 'Advanced', 'Director+']:
                if not job_experience_level_val:
                    job_experience_level_val = text
                    job_experience_level_el = el
            else:
                if not type_val:
                    type_val = text
                    type_el = el
        
        # qualifications
        quals_div = item.find('div', class_='Xsxa1e')
        quals_val = [li.text.strip() for li in quals_div.find_all('li')] if quals_div else []
        quals_el = quals_div
        
        fields_dict = {
            "title": {"value": title_val, "normalized": title_val},
            "url_offer": {"value": url_val, "normalized": url_val},
            "corporate_fare": {"value": corporate_fare_val, "normalized": corporate_fare_val},
            "place": {"value": place_val, "normalized": place_val},
            "type": {"value": type_val, "normalized": type_val},
            "job_experience_level": {"value": job_experience_level_val, "normalized": job_experience_level_val},
            "qualifications": {"value": quals_val if quals_val else None, "normalized": quals_val if quals_val else None}
        }
        
        elements_map = {
            "title": title_el,
            "url_offer": a_tag,
            "corporate_fare": corporate_fare_el,
            "place": place_el,
            "type": type_el,
            "job_experience_level": job_experience_level_el,
            "qualifications": quals_el
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
            "gold_record_id": f"WBV1_JOBS_GOOGLE_001_LISTING_{str(i+1).zfill(3)}",
            "fields": fields_dict,
            "provenance": provenance_dict
        }
        records.append(record)
        
    data = {
        "task_id": "WBV1_JOBS_GOOGLE_001_LISTING",
        "website_id": "google_careers",
        "schema_id": "job_listing_v1",
        "snapshot_id": snapshot_id,
        "snapshot_path": "raw_snapshots/jobs/google_careers_listing",
        "live_url": "https://www.google.com/about/careers/applications/jobs/results/",
        "annotation_metadata": {
            "annotation_version": "v1",
            "annotator_id": "ismail_khayoub",
            "verification_status": "human_verified",
            "total_records_extracted": len(records)
        },
        "records": records
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(records)} listing records to {json_path}")

if __name__ == "__main__":
    extract_listings()
