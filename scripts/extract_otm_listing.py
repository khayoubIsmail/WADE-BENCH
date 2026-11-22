import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_ONTHEMARKET_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_ONTHEMARKET_001_LISTING.json'
SNAP_ID = "SNAP_REAL_ONTHEMARKET_001_LISTING"

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

def clean_num(text):
    if text is None: return None
    text = str(text).replace(',', '').replace(' ', '')
    m = re.search(r'[\d]+', text)
    return int(re.sub(r'[^\d]', '', text)) if m else None

# Load WADE-bench Gold JSON
with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

# Extract Next.js data
next_data = soup.find('script', id='__NEXT_DATA__')
if not next_data:
    print("Could not find __NEXT_DATA__")
    exit(1)

data = json.loads(next_data.string)
rs = data.get('props', {}).get('initialReduxState', {})
listings = rs.get('results', {}).get('list', [])

def has_css_special_chars(cls):
    return any(c in cls for c in [':', '!', '[', ']', '/', '(', ')'])

def css_from_el(el):
    if not el or not el.name: return ""
    if el.get('id'): return f"{el.name}#{el['id']}"
    all_classes = el.get('class', [])
    safe_classes = [c for c in all_classes if not has_css_special_chars(c)]
    classes = safe_classes if safe_classes else all_classes
    if classes:
        return el.name + '.' + '.'.join(classes)
    return el.name

def build_css(el):
    if not el: return ""
    el_css = css_from_el(el)
    
    classes = el.get('class', [])
    matches = soup.find_all(el.name, class_=classes[0] if classes else None)
    if len(matches) <= 1:
        return el_css
    
    parent = el.parent
    if parent and parent.name and parent.name != '[document]':
        p_css = css_from_el(parent)
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

def find_dom_element(soup, val, key):
    if not val: return None
    
    # Try to find images/links first
    if key in ['listing_url', 'images_urls', 'agent_branding_logo']:
        v = val[0] if isinstance(val, list) else str(val)
        # remove domain for relative url matching
        v = v.replace('https://www.onthemarket.com', '')
        for el in soup.find_all(['a', 'img']):
            href = el.get('href') or el.get('src')
            if href and (v in href or href in v):
                return el

    # Text search
    v = str(val[0]) if isinstance(val, list) else str(val)
    candidates = soup.find_all(string=lambda t: t and v in t)
    for c in candidates:
        if c.parent.name not in ['script', 'style', 'option']:
            return c.parent
    return None

records = []
for idx, item in enumerate(listings):
    fields = {}
    provenance = {}
    
    def add(key, val, norm=None):
        if val is None or val == '': return
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
    
    # listing_url
    if item.get('details-url'):
        add('listing_url', 'https://www.onthemarket.com' + item['details-url'])
        
    # images_urls
    if item.get('images'):
        urls = [img.get('default') for img in item['images'] if img.get('default')]
        if urls:
            add('images_urls', urls, urls)
            
    # price
    price_val = item.get('price')
    if price_val:
        add('price', price_val, clean_num(price_val))
        
    # location
    address = item.get('address')
    if address:
        add('location', address)
        
    # type
    prop_type = item.get('humanised-property-type')
    if prop_type:
        add('type', prop_type)
        
    # bedrooms
    beds = item.get('bedrooms')
    if beds is not None:
        add('bedrooms', beds, clean_num(str(beds)))
        
    # bathrooms
    baths = item.get('bathrooms')
    if baths is not None:
        add('bathrooms', baths, clean_num(str(baths)))
        
    # key_features
    features = item.get('features')
    if features:
        add('key_features', features)
        
    # agent info
    agent = item.get('agent')
    if agent:
        if agent.get('name'):
            add('agent_branding', agent['name'])
        if agent.get('logo-url'):
            add('agent_branding_logo', agent['logo-url'])
        if agent.get('telephone'):
            add('phone', agent['telephone'], agent['telephone'].replace(' ', ''))
            
    # Email is typically not provided in the listing card for OnTheMarket
    # We leave it out or add null. WADE-bench is fine with missing fields.
            
    records.append({
        "gold_record_id": f"WBV1_REAL_ONTHEMARKET_001_LISTING_{idx+1:03d}",
        "fields": fields,
        "provenance": provenance
    })

out_data['records'] = records
out_data['annotation_metadata']['total_records_extracted'] = len(records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"Extraction completed. Extracted {len(records)} records.")
