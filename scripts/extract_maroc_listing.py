import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_MAROC_ANNONCES_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_MAROC_ANNONCES_001_LISTING.json'
SNAP_ID = "SNAP_REAL_MAROC_ANNONCES_001_LISTING"

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

def get_xpath(element):
    if not element: return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]': break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            try:
                index = siblings.index(child) + 1
                components.append(f"{child.name}[{index}]")
            except ValueError:
                components.append(child.name)
        child = parent
    components.reverse()
    return f"/{'/'.join(components)}"

def build_css(el):
    if not el: return ""
    if el.get('id'): return f"{el.name}#{el['id']}"
    classes = el.get('class', [])
    if classes: return f"{el.name}.{classes[0]}"
    
    path = [el.name]
    curr = el.parent
    while curr and curr.name != '[document]':
        if curr.get('id'):
            path.append(f"{curr.name}#{curr['id']}")
            break
        curr_classes = curr.get('class', [])
        if curr_classes:
            path.append(f"{curr.name}.{curr_classes[0]}")
            break
        path.append(curr.name)
        curr = curr.parent
        
    path.reverse()
    return " > ".join(path)

def prov(el, val):
    val_str = val if isinstance(val, str) else str(val)
    return {
        "snapshot_id": SNAP_ID,
        "css_selector": build_css(el),
        "xpath": get_xpath(el),
        "text_quote": val_str[:80]
    }

def clean_num(text):
    text = text.replace(' ', '')
    m = re.search(r'[\d]+', text)
    return int(re.sub(r'[^\d]', '', text)) if m else None

def normalize_date(text):
    text = text.lower()
    if 'aujourd\'hui' in text:
        time_m = re.search(r'(\d{2}:\d{2})', text)
        time_str = time_m.group(1) if time_m else "00:00"
        return f"2026-05-28T{time_str}:00"
    elif 'hier' in text:
        time_m = re.search(r'(\d{2}:\d{2})', text)
        time_str = time_m.group(1) if time_m else "00:00"
        return f"2026-05-27T{time_str}:00"
    else:
        # e.g., 26 Mai 2026 19:36
        m = re.search(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})\s+(\d{2}:\d{2})', text)
        if m:
            d, mo, y, t = m.groups()
            months = {'jan': '01', 'fev': '02', 'fév': '02', 'mars': '03', 'avr': '04', 'mai': '05', 'juin': '06', 'juil': '07', 'aout': '08', 'août': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12', 'déc': '12'}
            mo_num = next((v for k, v in months.items() if mo.startswith(k)), '01')
            return f"{y}-{mo_num}-{int(d):02d}T{t}:00"
    return None

with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

# Find listings (usually 20 per page as seen in earlier count)
listings = []
for li in soup.find_all('li'):
    if li.find('a') and li.find('h3') and li.find('div', class_='holder'):
        listings.append(li)

print(f"Found {len(listings)} listings")

records = []
for idx, li in enumerate(listings[:20]):
    fields = {}
    provenance = {}
    
    def add(key, val, el, norm=None):
        if not val or val == '': return
        fields[key] = {"value": val, "normalized": norm if norm is not None else val}
        provenance[key] = prov(el, val)
    
    # listing_url
    a_tag = li.find('a', href=True)
    if a_tag:
        href = a_tag['href']
        if not href.startswith('http'):
            href = 'https://www.marocannonces.com/' + href.lstrip('/')
        add('listing_url', href, a_tag)
        
    # image_url
    img = li.find('img', class_='lazy')
    if img:
        url = img.get('data-original') or img.get('src')
        if url:
            if not url.startswith('http'):
                url = 'https://www.marocannonces.com/' + url.lstrip('/')
            add('image_url', url, img)
            
    holder = li.find('div', class_='holder')
    if holder:
        # listing_title
        h3 = holder.find('h3')
        if h3:
            add('listing_title', h3.text.strip(), h3)
            
        # location
        loc = holder.find('span', class_='location')
        if loc:
            add('location', loc.text.strip(), loc)
            
        # price
        price = holder.find('strong', class_='price')
        if price:
            ptxt = price.text.strip()
            add('price', ptxt, price, clean_num(ptxt))
            
        # property_type
        views = holder.find('span', class_='views')
        if views:
            add('property_type', views.text.strip(), views)
            
    # published_date
    date_el = li.find('em', class_='date')
    if date_el:
        dtxt = ' '.join(date_el.stripped_strings)
        add('published_date', dtxt, date_el, normalize_date(dtxt))

    records.append({
        "gold_record_id": f"WBV1_REAL_MAROC_ANNONCES_001_LISTING_{idx+1:03d}",
        "fields": fields,
        "provenance": provenance
    })

out_data['records'] = records
out_data['annotation_metadata']['total_records_extracted'] = len(records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print("Extraction completed.")
