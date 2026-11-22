import json
import re
from bs4 import BeautifulSoup

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_REDFIN_001_LISTING.json'
html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_001_LISTING\page.html'
SNAP_ID = 'SNAP_REAL_REDFIN_001_LISTING'

soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def has_css_special_chars(cls):
    return ':' in cls or '!' in cls or '[' in cls or ']' in cls or '.' in cls or '{' in cls or '}' in cls

def css_from_el(el):
    if not el or not el.name: return ""
    if el.get('id'): 
        if el.name == 'a' and el.get('href') and not el['id'].startswith('ember'):
            return f"a#{el['id']}"
        elif el.name != 'a':
            return f"{el.name}#{el['id']}"
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

def build_css(el, container=None):
    if not el: return ""
    el_css = css_from_el(el)
    
    # If globally unique, return
    if el.get('id') or el.get('data-test'):
        all_matches = (container or soup).find_all(el.name, attrs={'data-test': el['data-test']}) if el.get('data-test') else (container or soup).find_all(id=el['id'])
        if len(all_matches) <= 1:
            return el_css
    else:
        classes = el.get('class', [])
        matches = (container or soup).find_all(el.name, class_=classes[0] if classes else None)
        if len(matches) <= 1:
            return el_css
            
    # Add nth-child to el if it has siblings of the same name
    parent = el.parent
    if parent and parent.name and parent.name != '[document]' and parent != container:
        siblings = [s for s in parent.children if hasattr(s, 'name') and s.name == el.name]
        if len(siblings) > 1:
            try:
                idx = siblings.index(el) + 1
                el_css = f"{el_css}:nth-child({idx})" if '[' in el_css or ':' in el_css else f"{el_css}:nth-of-type({idx})"
            except ValueError:
                pass
                
        p_css = build_css(parent, container)
        if p_css:
            return f"{p_css} > {el_css}"
        return el_css
    return el_css

def get_xpath(element, container=None):
    if not element: return None
    components = []
    child = element if element.name else element.parent
    while child and child.name and child.name != '[document]' and child != container:
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
    return "/".join(components)

cards = soup.find_all('div', class_=re.compile('MapHomeCardReact'))
if not cards:
    cards = soup.find_all('div', class_=re.compile('HomeCardContainer'))
if not cards:
    cards = soup.find_all('div', class_='HomeCard')

with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

base_id = out_data['records'][0]['gold_record_id'].rsplit('_', 1)[0]
records = []

for idx, card in enumerate(cards):
    fields = {}
    provenance = {}

    def add(key, val, el=None, container_relative=True):
        if not val: return
        fields[key] = {"value": val, "normalized": val}
        if el:
            if container_relative:
                # We prepend the card's CSS to the relative CSS
                c_css = build_css(card)
                r_css = build_css(el, container=card)
                css = f"{c_css} {r_css}" if r_css else c_css
                
                c_xpath = get_xpath(card)
                r_xpath = get_xpath(el, container=card)
                xpath = f"/{c_xpath}/{r_xpath}" if r_xpath else f"/{c_xpath}"
            else:
                css = build_css(el)
                xpath = f"/{get_xpath(el)}"
            provenance[key] = {
                "snapshot_id": SNAP_ID,
                "css_selector": css,
                "xpath": xpath,
                "text_quote": el.get_text(strip=True)[:80] if hasattr(el, 'get_text') else ""
            }

    # listing url
    a = card.find('a')
    if a and a.get('href'):
        add('listing_url', "https://www.redfin.com" + a.get('href'), a)

    # image url
    img = card.find('img')
    if img and img.get('src'):
        add('image_url', img.get('src'), img)

    # price
    price = card.find('span', class_='bp-Homecard__Price--value')
    if price:
        add('price', price.get_text(strip=True), price)

    # location
    addr = card.find('div', class_='bp-Homecard__Address')
    if addr:
        add('location', addr.get_text(strip=True), addr)

    # bedrooms
    beds = card.find('span', class_='bp-Homecard__Stats--beds')
    if beds:
        add('bedrooms', beds.get_text(strip=True), beds)

    # bathrooms
    baths = card.find('span', class_='bp-Homecard__Stats--baths')
    if baths:
        add('bathrooms', baths.get_text(strip=True), baths)

    # sq ft
    sqft = card.find('span', class_='bp-Homecard__Stats--sqft')
    if sqft:
        add('sq_ft', sqft.get_text(strip=True), sqft)

    # features
    features_el = card.find('div', class_='KeyFactsExtension')
    if features_el:
        features_list = [f.strip() for f in features_el.get_text(strip=True).split('•') if f.strip()]
        add('features', features_list, features_el)

    # listed by
    attr = card.find('div', class_='bp-Homecard__Attribution')
    if attr:
        attr_text = attr.get_text(strip=True)
        # Clean "Listing by Douglas Elliman Real Estate • Provided by RLS at REBNY"
        if attr_text.startswith('Listing by '):
            attr_text = attr_text[len('Listing by '):]
        if '•' in attr_text:
            attr_text = attr_text.split('•')[0].strip()
        add('listed_by', attr_text, attr)

    # open_time
    sashes = card.find_all('span', class_='bp-Homecard__Sash')
    for s in sashes:
        text = s.get_text(strip=True)
        if text.upper().startswith('OPEN'):
            # e.g., 'OPEN SUN, 1PM TO 2PM'
            # let's just extract the raw text or strip OPEN
            open_time = text.replace('OPEN ', '', 1)
            add('open_time', open_time, s)

    if not fields:
        continue

    rec = {
        "gold_record_id": f"{base_id}_{idx+1:03d}",
        "fields": fields,
        "provenance": provenance,
        "notes": "Extracted via script"
    }
    records.append(rec)

out_data['records'] = records
out_data['annotation_metadata']['total_records_extracted'] = len(records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"Extraction completed. Extracted {len(records)} records.")
