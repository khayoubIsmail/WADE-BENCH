import json
import re
import os
from bs4 import BeautifulSoup

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL.json'
html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
SNAP_ID = 'SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL'

soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def has_css_special_chars(cls):
    return ':' in cls or '!' in cls or '[' in cls or ']' in cls or '.' in cls

def css_from_el(el):
    if not el or not el.name: return ""
    if el.get('id'): 
        if el.name == 'a' and el.get('href') and not el['id'].startswith('ember'):
            return f"a#{el['id']}"
        elif el.name != 'a':
            return f"{el.name}#{el['id']}"
    if el.name == 'a' and el.get('href'):
        href = el['href']
        slug = href.replace('https://www.realestate.co.nz', '')
        parts = [p for p in slug.split('/') if p]
        if parts:
            return f'a[href*="/{parts[0]}/"]'
    if el.get('data-test'):
        return f"{el.name}[data-test='{el['data-test']}']"
    all_classes = el.get('class', [])
    seen = set()
    safe_classes = []
    for c in all_classes:
        if has_css_special_chars(c): continue
        if re.match(r'^\d', c): continue
        if c in seen: continue
        seen.add(c)
        safe_classes.append(c)
    classes = safe_classes if safe_classes else []
    if classes:
        return el.name + '.' + '.'.join(classes)
    return el.name

def build_css(el):
    if not el: return ""
    el_css = css_from_el(el)
    
    # If globally unique, return
    if el.get('id') or el.get('data-test'):
        all_matches = soup.find_all(el.name, attrs={'data-test': el['data-test']}) if el.get('data-test') else soup.find_all(id=el['id'])
        if len(all_matches) <= 1:
            return el_css
    else:
        classes = el.get('class', [])
        matches = soup.find_all(el.name, class_=classes[0] if classes else None)
        if len(matches) <= 1:
            return el_css
            
    # Add nth-child to el if it has siblings of the same name
    parent = el.parent
    if parent and parent.name and parent.name != '[document]':
        siblings = [s for s in parent.children if hasattr(s, 'name') and s.name == el.name]
        if len(siblings) > 1:
            try:
                idx = siblings.index(el) + 1
                el_css = f"{el_css}:nth-child({idx})" if '[' in el_css or ':' in el_css else f"{el_css}:nth-of-type({idx})"
            except ValueError:
                pass
                
        p_css = css_from_el(parent)
        
        # Also check if parent needs nth-child
        if parent.parent:
            gp_children = [s for s in parent.parent.children if hasattr(s, 'name') and s.name == parent.name]
            if len(gp_children) > 1:
                try:
                    idx = gp_children.index(parent) + 1
                    p_css = f"{p_css}:nth-child({idx})" if '[' in p_css else f"{p_css}:nth-of-type({idx})"
                except ValueError:
                    pass
                    
        return f"{p_css} > {el_css}"
    return el_css

def get_xpath(element):
    if not element: return None
    components = []
    child = element if element.name else element.parent
    while child and child.name and child.name != '[document]':
        parent = child.parent
        if parent is None or parent.name == '[document]':
            components.append(child.name)
            break
        siblings = [s for s in parent.children if hasattr(s, 'name') and s.name == child.name]
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

# Load WADE-bench Gold JSON
with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

base_record_template = out_data['records'][0]
base_id = base_record_template['gold_record_id']

fields = {}
provenance = {}

def add(key, val, el=None):
    if not val: return
    fields[key] = {"value": val, "normalized": val}
    if el:
        provenance[key] = {
            "snapshot_id": SNAP_ID,
            "css_selector": build_css(el),
            "xpath": get_xpath(el),
            "text_quote": el.get_text(strip=True)[:80] if hasattr(el, 'get_text') else ""
        }
    else:
        provenance[key] = {
            "snapshot_id": SNAP_ID,
            "css_selector": "html",
            "xpath": "/html",
            "text_quote": ""
        }

# images_urls
imgs = []
img_el = None
for btn in soup.find_all('button'):
    if btn.get('class') and 'media__photo' in btn.get('class'):
        img = btn.find('img')
        if img and img.get('src'):
            if not img_el:
                img_el = img
            src = img.get('src')
            # Clean URL: strip '.crop...' and append '.jpg'
            # e.g., 'https://.../abc.crop.191x105.jpg?options=compress' -> 'https://.../abc.jpg'
            if '.crop.' in src:
                src = src.split('.crop.')[0] + '.jpg'
            imgs.append(src)
if imgs:
    add('images_urls', imgs, img_el)

# location
h1 = soup.find('h1')
if h1:
    add('location', h1.get_text(strip=True), h1)

# listing url
canonical = soup.find('link', rel='canonical')
if canonical and canonical.get('href'):
    add('listing_url', canonical.get('href'), canonical)

# price
# The price is in an h3 with 'text-xl' next to the 'dollar' estimate icon
price_el = None
for h3 in soup.find_all('h3', class_='text-xl'):
    text = h3.get_text(strip=True)
    if '$' in text and 'K' in text:
        price_el = h3
        break

if price_el:
    add('price', price_el.get_text(strip=True), price_el)

# date_published (not present on off-market)
# Will skip unless found

# features (bedrooms, bathrooms, floor_area, land_area, parking_or_garage_spaces)
def find_feature(name):
    el = soup.find('title', string=re.compile(name, re.IGNORECASE))
    if el:
        svg = el.parent
        svg_container = svg.parent
        feature_container = svg_container.parent
        val = feature_container.get_text(strip=True).replace(el.get_text(strip=True), '').strip()
        # Ensure we only return the value if it's not empty
        if val:
            return val, feature_container
    return None, None

v, el = find_feature('Bedroom')
if v: add('bedrooms', v, el)

v, el = find_feature('Bathroom')
if v: add('bathrooms', v, el)

v, el = find_feature('Floor area')
if v: add('floor_area', v, el)

v, el = find_feature('Land area')
if v: add('land_area', v, el)

v, el = find_feature('Garage')
if v: add('parking_or_garage_spaces', v, el)

# Update records
out_data['records'] = [{
    "gold_record_id": base_id,
    "fields": fields,
    "provenance": provenance,
    "notes": "Extracted via script"
}]

# Write out JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print("Extraction completed. Updated fields:", list(fields.keys()))
