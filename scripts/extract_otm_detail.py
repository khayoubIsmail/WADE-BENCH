import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_ONTHEMARKET_002_DETAIL\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_ONTHEMARKET_002_DETAIL.json'
SNAP_ID = "SNAP_REAL_ONTHEMARKET_002_DETAIL"

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

def clean_num(text):
    if text is None: return None
    text = str(text).replace(',', '').replace(' ', '')
    m = re.search(r'[\d\.]+', text)
    if m:
        try:
            return int(float(re.sub(r'[^\d\.]', '', text)))
        except ValueError:
            pass
    return None

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

def has_css_special_chars(cls):
    """Return True if class name contains chars that need CSS escaping (Tailwind responsive prefixes, etc.)"""
    return any(c in cls for c in [':', '!', '[', ']', '/', '(', ')'])

def css_from_el(el):
    if not el or not el.name: return ""
    if el.get('id'): return f"{el.name}#{el['id']}"
    all_classes = el.get('class', [])
    # Prefer classes without special chars; fall back to all if none are clean
    safe_classes = [c for c in all_classes if not has_css_special_chars(c)]
    classes = safe_classes if safe_classes else all_classes
    if classes:
        return el.name + '.' + '.'.join(classes)
    return el.name

def build_css(el):
    if not el: return ""
    el_css = css_from_el(el)
    
    # Check if this selector is unique on the page
    classes = el.get('class', [])
    matches = soup.find_all(el.name, class_=classes[0] if classes else None)
    if len(matches) <= 1:
        return el_css
    
    # Not unique — add parent context with :nth-of-type to disambiguate
    parent = el.parent
    if parent and parent.name and parent.name != '[document]':
        p_css = css_from_el(parent)
        # Find which nth-of-type this parent is among its siblings
        if parent.parent:
            gp_children = [s for s in parent.parent.children if hasattr(s, 'name') and s.name == parent.name]
            if len(gp_children) > 1:
                try:
                    idx = gp_children.index(parent) + 1
                    return f"{p_css}:nth-of-type({idx}) > {el_css}"
                except ValueError:
                    pass
        return f"{p_css} > {el_css}"
    
    return el_css

def find_dom_element(soup, val, key):
    if not val: return None

    # Key-specific DOM targeting
    if key == 'listing_url':
        v = str(val).replace('https://www.onthemarket.com', '')
        for el in soup.find_all('a'):
            if el.get('href') and v in el.get('href', ''):
                return el

    elif key == 'images_urls':
        v = val[0] if isinstance(val, list) else str(val)
        path = v.replace('https://media.onthemarket.com', '')
        for el in soup.find_all('img'):
            if el.get('src') and path in el.get('src', ''):
                return el

    elif key in ('agent_logo', 'floorplan_url'):
        v = val[0] if isinstance(val, list) else str(val)
        v = v.replace('https://media.onthemarket.com', '')
        for el in soup.find_all('img'):
            if el.get('src') and v in el.get('src', ''):
                return el

    elif key == 'price':
        for el in soup.find_all(['span', 'div', 'p', 'strong']):
            if el.get_text(strip=True) == str(val) or el.get_text(strip=True).startswith(str(val)):
                if el.name not in ['title']:
                    return el

    elif key == 'title':
        for el in soup.find_all('h1'):
            if str(val).strip() in el.get_text(strip=True):
                return el

    elif key == 'location':
        for el in soup.find_all(['p', 'span', 'address', 'h2']):
            if el.get_text(strip=True) == str(val):
                return el

    elif key == 'type':
        for el in soup.find_all(['div', 'span', 'p']):
            if el.get_text(strip=True) == str(val):
                return el

    elif key == 'bedrooms':
        for el in soup.find_all('div'):
            classes = el.get('class', [])
            if 'leading-none' in classes and 'whitespace-nowrap' in classes:
                txt = el.get_text(strip=True)
                if 'bed' in txt.lower() and str(val) in txt:
                    return el

    elif key == 'bathrooms':
        for el in soup.find_all('div'):
            classes = el.get('class', [])
            if 'leading-none' in classes and 'whitespace-nowrap' in classes:
                txt = el.get_text(strip=True)
                if 'bath' in txt.lower() and str(val) in txt:
                    return el

    elif key == 'sq_ft':
        for el in soup.find_all(['span', 'strong', 'div']):
            if el.get_text(strip=True) == str(val):
                parent_txt = el.parent.get_text(strip=True).lower() if el.parent else ''
                if 'sq' in parent_txt or 'ft' in parent_txt or 'area' in parent_txt:
                    return el

    elif key == 'EPC_rating':
        for el in soup.find_all(['span', 'strong', 'div']):
            txt = el.get_text(strip=True)
            if txt == str(val) and el.parent:
                parent_txt = el.parent.get_text(strip=True).lower()
                if 'epc' in parent_txt or 'energy' in parent_txt or 'rating' in parent_txt:
                    return el

    elif key == 'agent':
        for el in soup.find_all(['div', 'span', 'a', 'h2', 'h3']):
            if el.get_text(strip=True) == str(val):
                return el

    elif key == 'agent_phone':
        for el in soup.find_all(['a', 'span', 'div']):
            if str(val) in el.get_text(strip=True):
                if el.get('href', '').startswith('tel:') or len(el.get_text(strip=True)) < 30:
                    return el

    elif key == 'Council_tax':
        for el in soup.find_all(['span', 'div', 'td']):
            if str(val) in el.get_text(strip=True) and len(el.get_text(strip=True)) < 30:
                return el

    elif key in ('Features_description', 'Property_information'):
        # The description is HTML - look for the first feature text in DOM
        features = val.get('features', []) if isinstance(val, dict) else []
        if features and features[0].get('feature'):
            first_feat = features[0]['feature']
            for el in soup.find_all(['li', 'span', 'div']):
                if el.get_text(strip=True) == first_feat:
                    return el
        return None  # fallback to JSON

    elif key == 'About_agent':
        return None  # agent description only in JSON

    elif key == 'Nearest_stations':
        first = val[0] if isinstance(val, list) else str(val)
        name = first.split(' (')[0]  # strip distance part
        for el in soup.find_all(['span', 'div', 'a']):
            if el.get_text(strip=True) == name:
                return el

    elif key in ('Area_statistics', 'map', 'Mobile_signal', 'agent_website'):
        return None  # These are best served from JSON

    # Generic fallback text search (avoid head/script/style)
    v = str(val[0]) if isinstance(val, list) else str(val)
    if len(v) > 120: v = v[:80]
    candidates = soup.find_all(string=lambda t: t and v in t)
    for c in candidates:
        if c.parent.name not in ['script', 'style', 'option', 'title', 'head']:
            return c.parent
    return None


# Load WADE-bench Gold JSON
with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

# Extract Next.js data
next_data = soup.find('script', id='__NEXT_DATA__')
if not next_data:
    print("Could not find __NEXT_DATA__")
    exit(1)

data = json.loads(next_data.string)
prop_dict = data.get('props', {}).get('initialReduxState', {}).get('property', {})

fields = {}
provenance = {}

def add(key, val, norm=None):
    if val is None or val == '': return
    # normalize empty lists
    if isinstance(val, list) and not val: return
    
    fields[key] = {"value": val, "normalized": norm if norm is not None else val}
    
    el = find_dom_element(soup, val, key)
    if el:
        provenance[key] = {
            "snapshot_id": SNAP_ID,
            "css_selector": build_css(el),
            "xpath": get_xpath(el),
            "text_quote": el.get_text(strip=True)[:80] if hasattr(el, 'get_text') else str(val)[:80]
        }
    else:
        provenance[key] = {
            "snapshot_id": SNAP_ID,
            "css_selector": "script#__NEXT_DATA__",
            "xpath": "//script[@id='__NEXT_DATA__']",
            "text_quote": str(val)[:80]
        }

# mapping
if prop_dict.get('canonicalUrl'):
    add('listing_url', prop_dict['canonicalUrl'])

if prop_dict.get('images'):
    imgs = [img.get('largeUrl') for img in prop_dict['images'] if img.get('largeUrl')]
    if imgs: add('images_urls', imgs)

if prop_dict.get('floorplans'):
    fps = [f.get('file') for f in prop_dict['floorplans'] if f.get('file')]
    if fps: add('floorplan_url', fps)

loc = prop_dict.get('location')
if loc and 'lat' in loc and 'lon' in loc:
    add('map', {"latitude": loc['lat'], "longitude": loc['lon']})

area_stats = prop_dict.get('areaStats')
if area_stats:
    add('Area_statistics', area_stats)

price = prop_dict.get('price')
if price:
    add('price', price, clean_num(price))

title = prop_dict.get('propertyTitle') or prop_dict.get('propertySerpTitle')
if title: add('title', title)

displayAddress = prop_dict.get('displayAddress')
if displayAddress: add('location', displayAddress)

type_str = prop_dict.get('humanisedPropertyType')
if type_str: add('type', type_str)

beds = prop_dict.get('bedrooms')
if beds is not None: add('bedrooms', beds, clean_num(str(beds)))

baths = prop_dict.get('bathrooms')
if baths is not None: add('bathrooms', baths, clean_num(str(baths)))

sqft = prop_dict.get('minimumAreaSqFt') or prop_dict.get('minimumArea')
if sqft is not None: add('sq_ft', sqft, clean_num(str(sqft)))

epc = prop_dict.get('epc', {}).get('rating')
if epc: add('EPC_rating', epc)

agent = prop_dict.get('agent', {})
if agent.get('name'): add('agent', agent['name'])
if agent.get('logoUrl'): add('agent_logo', agent['logoUrl'])
if agent.get('telephone'): add('agent_phone', agent['telephone'], agent['telephone'].replace(' ', ''))
if agent.get('websiteUrl'): add('agent_website', agent['websiteUrl'])
if agent.get('description'): add('About_agent', agent['description'])

key_info = prop_dict.get('keyInfo', [])
for info in key_info:
    if info.get('title') == 'Council tax':
        add('Council_tax', info.get('value'))
    elif info.get('title') == 'Mobile signal':
        mobile_data = info.get('data', {})
        # Format as an array
        arr = []
        for network in ['o2', 'three', 'vodafone', 'ee']:
            if network in mobile_data:
                arr.append(f"{network}: {mobile_data[network]}")
        if arr:
            add('Mobile_signal', arr)

features = prop_dict.get('features')
description = prop_dict.get('description')
if features or description:
    fd = {
        "features": features,
        "description": description
    }
    add('Features_description', fd)

# Add Property information from this agent (usually the same as description)
if description:
    add('Property_information', description)

stations = prop_dict.get('station')
if stations:
    st_names = [f"{s.get('name')} ({s.get('displayDistance')})" if s.get('displayDistance') else s.get('name') for s in stations if s.get('name')]
    if st_names:
        add('Nearest_stations', st_names)

original_record = out_data['records'][0]
out_data['records'] = [{
    "gold_record_id": original_record['gold_record_id'],
    "fields": fields,
    "provenance": provenance
}]
out_data['annotation_metadata']['total_records_extracted'] = 1

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"Extraction completed. Extracted {len(fields)} fields.")
