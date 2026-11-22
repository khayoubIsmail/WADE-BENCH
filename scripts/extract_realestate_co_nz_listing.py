import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_REALESTATE.CO.NZ_001_LISTING.json'
SNAP_ID = "SNAP_REAL_REALESTATE.CO.NZ_001_LISTING"

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

def has_css_special_chars(cls):
    # Filter Tailwind classes with responsive prefixes, arbitrary values, dots or fractional sizes
    if any(c in cls for c in [':', '!', '[', ']', '/', '(', ')']): return True
    if '.' in cls: return True  # e.g. text-xs.5, md:text-sm.5, pl-3.5
    return False

def css_from_el(el):
    if not el or not el.name: return ""
    if el.get('id'): 
        # Avoid dynamic ember IDs like ember105 - use href instead for anchors
        if el.name == 'a' and el.get('href') and not el['id'].startswith('ember'):
            return f"a#{el['id']}"
        elif el.name != 'a':
            return f"{el.name}#{el['id']}"
    # For anchors with href, produce a stable href-based selector
    if el.name == 'a' and el.get('href'):
        # Use a short unique path segment from the href
        href = el['href']
        slug = href.replace('https://www.realestate.co.nz', '')
        # Take first path segment e.g. /43058090/
        parts = [p for p in slug.split('/') if p]
        if parts:
            return f'a[href*="/{parts[0]}/"]'
    if el.get('data-test'):
        # Ensure we output valid single-quoted string to avoid json escaping issues
        return f"{el.name}[data-test='{el['data-test']}']"
    all_classes = el.get('class', [])
    # Filter special chars, deduplicate, remove digit-only or digit-starting classes
    seen = set()
    safe_classes = []
    for c in all_classes:
        if has_css_special_chars(c): continue
        if re.match(r'^\d', c): continue  # skip classes starting with digit (e.g. '5', '3.5')
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
    
    # Check if el_css is globally unique — if so, no parent context needed
    if el.get('id') or el.get('data-test'):
        all_matches = soup.find_all(el.name, attrs={'data-test': el['data-test']}) if el.get('data-test') else soup.find_all(id=el['id'])
        if len(all_matches) <= 1:
            return el_css
    else:
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
                    # :nth-of-type does NOT work with attribute selectors [attr=val]
                    # Use :nth-child instead, which is valid in standard CSS
                    if '[' in p_css:
                        return f"{p_css}:nth-child({idx}) > {el_css}"
                    else:
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
    
    if key == 'listing_url':
        v = str(val).replace('https://www.realestate.co.nz', '')
        # Return the card anchor - it has a stable href attribute
        for el in soup.find_all('a'):
            href = el.get('href', '')
            if v in href and el.find(['h3', 'h4']):
                return el

    elif key in ('images_urls', 'agent_branding_negotiator_pic'):
        v = val[0] if isinstance(val, list) else str(val)
        m = re.search(r'([a-f0-9]{32})', v)
        search_v = m.group(1) if m else v
        for el in soup.find_all('img'):
            if el.get('src') and search_v in el.get('src', ''):
                return el

    elif key == 'agent_branding_logo':
        v = val[0] if isinstance(val, list) else str(val)
        m = re.search(r'([a-f0-9]{32})', v)
        search_v = m.group(1) if m else v
        for el in soup.find_all('img'):
            src = el.get('src', '')
            if search_v in src:
                return el
        return None  # keep original base-url, not found in DOM

    elif key == 'price':
        for el in soup.find_all(['span', 'div', 'p']):
            if el.get_text(strip=True) == str(val):
                return el

    elif key == 'title':
        # Title is in an h4 on the listing card
        for el in soup.find_all('h4'):
            if el.get_text(strip=True) == str(val):
                return el
        for el in soup.find_all(['h2', 'h3', 'h5']):
            if el.get_text(strip=True) == str(val):
                return el

    elif key == 'location':
        # Location is in an h3
        for el in soup.find_all('h3'):
            if el.get_text(strip=True) == str(val):
                return el
        for el in soup.find_all(['span', 'div', 'p']):
            if el.get_text(strip=True) == str(val):
                return el

    elif key == 'bedrooms':
        # Use data-test="bedroom" attribute
        str_val = str(val)
        for el in soup.find_all(attrs={'data-test': 'bedroom'}):
            if el.get_text(strip=True) == str_val:
                return el

    elif key == 'bathrooms':
        str_val = str(val)
        for el in soup.find_all(attrs={'data-test': 'bathroom'}):
            if el.get_text(strip=True) == str_val:
                return el

    elif key == 'area':
        # Area is inside a features__item container; find the one with m2 text
        str_val = str(val)  # e.g. "515m2"
        for el in soup.find_all(attrs={'data-test': 'tile__search-result__content__features__item'}):
            if el.get_text(strip=True) == str_val:
                return el
        # fallback: bare div/span
        for el in soup.find_all(['div', 'span']):
            if el.get_text(strip=True) == str_val:
                return el

    elif key == 'property_type':
        # Property type is a div with specific classes
        str_val = str(val)
        for el in soup.find_all('div', class_='line-clamp-1'):
            if el.get_text(strip=True) == str_val:
                return el

    elif key in ('agent_branding', 'agent_branding_negotiator_name'):
        names = val if isinstance(val, list) else [val]
        for name in names:
            # Agent names in DOM may have trailing comma e.g. "Kris Gray,"
            for el in soup.find_all('div', class_='line-clamp-1'):
                txt = el.get_text(strip=True)
                if txt == name or txt.rstrip(',') == name:
                    return el

    return None

# Locate state script
scripts = soup.find_all('script')
data_str = None
state_script_el = None
for s in scripts:
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data_str = s.string
        state_script_el = s
        break

if not data_str:
    print("Could not find JSON state")
    exit(1)

data = json.loads(data_str)
queries = data.get('queries', {})
q_data = None
for qk, qv in queries.items():
    if 'page[limit]=20' in qk:
        q_data = json.loads(qv)
        break

if not q_data:
    print("Could not find listing query")
    exit(1)

listings = q_data.get('data', [])
included = {i['id']: i for i in q_data.get('included', [])}

# Load WADE-bench Gold JSON
with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

# Keep the base structure for the first record to duplicate
base_record_template = out_data['records'][0]
base_id = base_record_template['gold_record_id'].rsplit('_', 1)[0]
records = []

for idx, listing in enumerate(listings):
    attr = listing.get('attributes', {})
    rel = listing.get('relationships', {})
    
    fields = {}
    provenance = {}

    # Find the listing's DOM card element (scoped to correct listing card)
    listing_url = attr.get('website-full-url', '')
    card_el = None
    if listing_url:
        slug = listing_url.replace('https://www.realestate.co.nz', '')
        for a in soup.find_all('a', href=True):
            if slug in a.get('href', '') and a.find(['h3', 'h4']):
                card_el = a
                break

    # Skip listings not rendered in the DOM (lazy-loaded, not in snapshot)
    if not card_el:
        continue

    card_soup = card_el  # always scoped to card

    # Fields scoped to card; others search full soup
    CARD_SCOPED_KEYS = {'title', 'location', 'price', 'bedrooms', 'bathrooms', 'area', 'property_type'}

    def add(key, val, norm=None):
        if val is None or val == '': return
        if isinstance(val, list) and not val: return
        
        fields[key] = {"value": val, "normalized": norm if norm is not None else val}
        
        search_scope = card_soup if (card_el and key in CARD_SCOPED_KEYS) else soup
        el = find_dom_element(search_scope, val, key)
        if el:
            provenance[key] = {
                "snapshot_id": SNAP_ID,
                "css_selector": build_css(el),
                "xpath": get_xpath(el),
                "text_quote": el.get_text(strip=True)[:80] if hasattr(el, 'get_text') else str(val)[:80]
            }
        else:
            # Fallback to JSON script
            provenance[key] = {
                "snapshot_id": SNAP_ID,
                "css_selector": build_css(state_script_el) if state_script_el else "script",
                "xpath": get_xpath(state_script_el) if state_script_el else "//script",
                "text_quote": str(val)[:80]
            }

    # Extract fields
    photos = attr.get('photos')
    if photos:
        photo_urls = [f"https://mediaserver.realestate.co.nz{p.get('base-url')}.jpg" for p in photos if p.get('base-url')]
        if photo_urls:
            add('images_urls', photo_urls)
        
    url = attr.get('website-full-url')
    if url: add('listing_url', url)

    header = attr.get('header')
    if header: add('title', header)

    address = attr.get('address', {})
    if address.get('display-address'):
        add('location', address['display-address'])
    elif address.get('full-address'):
        add('location', address['full-address'])

    price = attr.get('price-display')
    if price: add('price', price, clean_num(price))

    beds = attr.get('bedroom-count')
    if beds is not None: add('bedrooms', beds, clean_num(beds))

    baths = attr.get('bathroom-count')
    if baths is not None: add('bathrooms', baths, clean_num(baths))

    l_area = attr.get('land-area')
    f_area = attr.get('floor-area')
    if l_area:
        add('area', f"{l_area}m2", clean_num(l_area))
    elif f_area:
        add('area', f"{f_area}m2", clean_num(f_area))

    prop_type = attr.get('listing-sub-type')
    if prop_type: add('property_type', prop_type)

    features_dict = attr.get('features')
    if features_dict:
        feature_list = []
        if features_dict.get('pool'): feature_list.append("Pool")
        if features_dict.get('garages', 0) > 0: feature_list.append(f"{features_dict['garages']} Garages")
        if features_dict.get('carports', 0) > 0: feature_list.append(f"{features_dict['carports']} Carports")
        if features_dict.get('storey-count', 0) > 0: feature_list.append(f"{features_dict['storey-count']} Storeys")
        
        other_features = features_dict.get('other-features', {})
        if isinstance(other_features, dict):
            for k, v in other_features.items():
                if v: feature_list.append(str(k))
        elif isinstance(other_features, list):
            feature_list.extend(str(item) for item in other_features)
            
        if feature_list:
            add('features', feature_list)

    # Agents and offices
    agent_names = []
    agent_pics = []
    agent_ids = [a['id'] for a in rel.get('agents', {}).get('data', [])]
    for aid in agent_ids:
        agent = included.get(aid, {}).get('attributes', {})
        name = f"{agent.get('first-name', '')} {agent.get('last-name', '')}".strip()
        if name: agent_names.append(name)
        img = agent.get('image')
        if img:
            if isinstance(img, dict) and img.get('base-url'):
                agent_pics.append(f"https://mediaserver.realestate.co.nz{img.get('base-url')}.jpg")
            elif isinstance(img, str):
                agent_pics.append(img if img.startswith('http') else f"https://mediaserver.realestate.co.nz{img}.jpg")
        
    if agent_names: add('agent_branding_negotiator_name', agent_names)
    if agent_pics: add('agent_branding_negotiator_pic', agent_pics)
        
    office_names = []
    office_logos = []
    office_ids = [o['id'] for o in rel.get('offices', {}).get('data', [])]
    for oid in office_ids:
        office = included.get(oid, {}).get('attributes', {})
        # Use colloquial-name if available (shorter, matches what DOM shows)
        name = office.get('colloquial-name') or office.get('name')
        if name: office_names.append(name)
        imgs = office.get('images')
        if imgs:
            if isinstance(imgs, list) and len(imgs) > 0 and isinstance(imgs[0], dict) and imgs[0].get('base-url'):
                office_logos.append(f"https://mediaserver.realestate.co.nz{imgs[0].get('base-url')}.jpg")
            elif isinstance(imgs, dict) and imgs.get('base-url'):
                office_logos.append(f"https://mediaserver.realestate.co.nz{imgs.get('base-url')}.jpg")
            elif isinstance(imgs, str):
                office_logos.append(imgs if imgs.startswith('http') else f"https://mediaserver.realestate.co.nz{imgs}.jpg")
        
    if office_names: add('agent_branding', office_names)
    if office_logos: add('agent_branding_logo', office_logos)

    record_id = f"{base_id}_{str(idx+1).zfill(3)}"
    records.append({
        "gold_record_id": record_id,
        "fields": fields,
        "provenance": provenance
    })

out_data['records'] = records
out_data['annotation_metadata']['total_records_extracted'] = len(records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"Extraction completed. Extracted {len(records)} records.")
