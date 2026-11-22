import json
import re
from bs4 import BeautifulSoup

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_REDFIN_002_DETAIL.json'
html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_002_DETAIL\page.html'
SNAP_ID = 'SNAP_REAL_REDFIN_002_DETAIL'

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
    if el.get('data-rf-test-id'):
        return f"{el.name}[data-rf-test-id='{el['data-rf-test-id']}']"
    if el.get('data-rf-test-name'):
        return f"{el.name}[data-rf-test-name='{el['data-rf-test-name']}']"
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
    
    if el.get('id') or el.get('data-rf-test-id') or el.get('data-rf-test-name'):
        attrs = {}
        if el.get('data-rf-test-id'): attrs['data-rf-test-id'] = el['data-rf-test-id']
        elif el.get('data-rf-test-name'): attrs['data-rf-test-name'] = el['data-rf-test-name']
        all_matches = (container or soup).find_all(el.name, attrs=attrs) if attrs else (container or soup).find_all(id=el['id'])
        if len(all_matches) <= 1:
            return el_css
    else:
        classes = el.get('class', [])
        matches = (container or soup).find_all(el.name, class_=classes[0] if classes else None)
        if len(matches) <= 1:
            return el_css
            
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
            "xpath": "/" + get_xpath(el),
            "text_quote": el.get_text(strip=True)[:80] if hasattr(el, 'get_text') else ""
        }
    else:
        provenance[key] = {
            "snapshot_id": SNAP_ID,
            "css_selector": "html",
            "xpath": "/html",
            "text_quote": ""
        }

# listing url
canonical = soup.find('link', rel='canonical')
if canonical and canonical.get('href'):
    add('listing_url', canonical.get('href'), canonical)

# image url
img = soup.find('span', id='MBImage')
if img: img = img.find('img')
if not img: img = soup.find('img', class_='Photo--image')
if not img: img = soup.find('img', {'data-rf-test-id': 'photoPrimary'})
if not img: img = soup.find('img', class_=re.compile('img-card'))
if not img: img = soup.find('div', class_='photo-container').find('img') if soup.find('div', class_='photo-container') else None
if img and img.get('src'):
    add('image_url', img.get('src'), img)

# status
status_el = soup.find('span', string=re.compile('Status', re.IGNORECASE))
if status_el and status_el.parent:
    status_val = status_el.parent.find('span', class_='value') or status_el.parent.parent.find('span', class_='value')
    if status_val: add('status', status_val.get_text(strip=True), status_val)

if 'status' not in fields:
    # Try React InitialContext
    import json
    m = re.search(r'root\.__reactServerState\.InitialContext = (\{.*?\});', soup.decode(), re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            cache = data.get('ReactServerAgent.cache', {}).get('dataCache', {})
            for k, v in cache.items():
                if 'listingStatusBannerInfo' in k and 'res' in v and 'text' in v['res']:
                    res_text = v['res']['text']
                    res_json = json.loads(res_text.split('&&')[-1])
                    if 'payload' in res_json:
                        segs = res_json['payload'].get('segments', [])
                        if segs:
                            add('status', segs[0].get('text', 'For sale'), soup.find('body'))
        except Exception:
            pass

# Helper for table values
def get_table_val(label_str):
    lbl = soup.find('span', class_='table-label', string=re.compile(label_str, re.IGNORECASE))
    if lbl and lbl.parent:
        return lbl.parent.find('span', class_='table-value') or lbl.parent.find('div', class_='table-value') or lbl.find_next_sibling('span') or lbl.find_next_sibling('div')
    return None

# price
price = soup.find('div', {'data-rf-test-id': 'abp-price'})
if price: add('price', price.get_text(strip=True), price)
else:
    lbl = soup.find('div', class_='panel-title', string=re.compile('Home price', re.IGNORECASE))
    if lbl:
        val = lbl.find_next_sibling('div', class_='panel-value')
        if val:
            add('price', val.get_text(strip=True), val)

# bedrooms
beds = soup.find('div', {'data-rf-test-id': 'abp-beds'})
if beds: add('bedrooms', beds.get_text(strip=True), beds)
else:
    bed_val = get_table_val('Beds')
    if bed_val and bed_val.get_text(strip=True) and bed_val.get_text(strip=True) != '—': add('bedrooms', bed_val.get_text(strip=True), bed_val)

# bathrooms
baths = soup.find('div', {'data-rf-test-id': 'abp-baths'})
if baths: add('bathrooms', baths.get_text(strip=True), baths)
else:
    bath_val = get_table_val('Baths')
    if bath_val and bath_val.get_text(strip=True) and bath_val.get_text(strip=True) != '—': add('bathrooms', bath_val.get_text(strip=True), bath_val)

# sq_ft
sqft = soup.find('div', {'data-rf-test-id': 'abp-sqFt'})
if sqft: add('sq_ft', sqft.get_text(strip=True), sqft)
else:
    sq_val = get_table_val('Total Sq. Ft.')
    if sq_val and sq_val.get_text(strip=True) and sq_val.get_text(strip=True) != '—': add('sq_ft', sq_val.get_text(strip=True), sq_val)

# location
h1 = soup.find('h1')
if h1: add('location', h1.get_text(strip=True), h1)

# type, year built, lot size, price per sq ft, parking
key_details = soup.find_all('div', class_='keyDetail')
for kd in key_details:
    text = kd.get_text(" ", strip=True).lower()
    if 'type' in text and not 'property type' in text:
        add('type', kd.find('span', class_='value').get_text(strip=True) if kd.find('span', class_='value') else kd.get_text(strip=True), kd)
    elif 'year built' in text:
        add('year_built', kd.find('span', class_='value').get_text(strip=True) if kd.find('span', class_='value') else kd.get_text(strip=True), kd)
    elif 'lot size' in text:
        add('lot_size', kd.find('span', class_='value').get_text(strip=True) if kd.find('span', class_='value') else kd.get_text(strip=True), kd)
    elif 'price/sq.ft.' in text:
        add('price_per_sq_ft', kd.find('span', class_='value').get_text(strip=True) if kd.find('span', class_='value') else kd.get_text(strip=True), kd)
    elif 'garage' in text or 'parking' in text:
        add('parking', kd.find('span', class_='value').get_text(strip=True) if kd.find('span', class_='value') else kd.get_text(strip=True), kd)

# Fallback to table for type, year built, lot size, parking
if 'type' not in fields:
    val = get_table_val('Style')
    if val and val.get_text(strip=True) != '—': add('type', val.get_text(strip=True), val)
if 'year_built' not in fields:
    val = get_table_val('Year built')
    if val and val.get_text(strip=True) != '—': add('year_built', val.get_text(strip=True), val)
if 'lot_size' not in fields:
    val = get_table_val('Lot size')
    if val and val.get_text(strip=True) != '—': add('lot_size', val.get_text(strip=True), val)
if 'parking' not in fields:
    val = get_table_val('Garage') or get_table_val('Parking Spaces')
    if val and val.get_text(strip=True) != '—': add('parking', val.get_text(strip=True), val)

# listed_by (array)
agents = soup.find_all('div', class_='agent-info-item')
if agents:
    names = []
    for a in agents:
        text = a.get_text(" | ", strip=True)
        # e.g., "Listing by | Tyrone Byrdsong | • | YourHomeSold Guaranteed Realty"
        parts = [p.strip() for p in text.replace('•', '|').replace('\u2022', '|').split('|')]
        for p in parts:
            if p and p.lower() not in ['listing by', 'provided by', 'redfin']:
                if p not in names: names.append(p)
    if names:
        # Just use the first agent-info-item as the provenance element
        add('listed_by', names, agents[0])

# Sections: About_this_home, Property details, Public record
def extract_section(title, field_name):
    el = soup.find(string=lambda t: t and title.lower() in t.lower())
    if el:
        p = el.parent
        while p and p.name != 'div' and p.name != 'section':
            p = p.parent
        if p:
            add(field_name, p.get_text(" ", strip=True)[:500], p)

extract_section('About this home', 'about_this_home')
# Public record
pr_h2 = soup.find('h2', string=re.compile('Public record', re.IGNORECASE))
if pr_h2:
    pr_parent = pr_h2.parent
    while pr_parent and pr_parent.name != 'section':
        pr_parent = pr_parent.parent
    if pr_parent:
        pr_data = {}
        for row in pr_parent.find_all('div', class_='table-row'):
            label = row.find('span', class_='table-label')
            value = row.find('div', class_='table-value')
            if label and value:
                lbl_text = label.get_text(strip=True)
                val_text = value.get_text(strip=True).replace('\u2022', '|')
                pr_data[lbl_text] = val_text
        if pr_data:
            add('public_record', pr_data, pr_parent)
        
# property_details
interior_data = {}
exterior_data = {}
sg_divs = soup.find_all('div', class_='super-group-content')
for div in sg_divs:
    section_data = {}
    is_exterior = False
    for h in div.find_all('li', class_='propertyDetailsHeader'):
        span = h.find('span')
        if span:
            header_text = span.get_text(strip=True)
            if 'exterior' in header_text.lower():
                is_exterior = True
            items = []
            for li in h.find_next_siblings('li', class_='entryItem'):
                items.append(li.get_text(strip=True).replace('\u2022', '|'))
            section_data[header_text] = items
    if is_exterior:
        exterior_data.update(section_data)
    else:
        interior_data.update(section_data)

property_details_data = [
    {"interior": interior_data if interior_data else None},
    {"exterior": exterior_data if exterior_data else None}
]

prop_el = soup.find(string=lambda t: t and 'Property details' in t)
if prop_el:
    add('property_details', property_details_data, prop_el.parent)
else:
    add('property_details', property_details_data, soup.find('body'))

# around_this_home
schools = []
for li in soup.find_all('div', class_='SchoolsListItem'):
    name_el = li.find('div', class_='SchoolsListItem__heading')
    desc_el = li.find('p', class_='SchoolsListItem__description')
    rating_el = li.find('span', class_='SchoolsListItem__schoolRating')
    
    school_obj = {}
    if name_el: school_obj["name"] = name_el.get_text(strip=True)
    if desc_el: school_obj["description"] = desc_el.get_text(strip=True).replace('\u2022', '|')
    if rating_el: school_obj["rating"] = rating_el.get_text(strip=True)
    
    if school_obj:
        schools.append(school_obj)

places = []
transit = []

# Extract places and transit from React state
import json
m = re.search(r'root\.__reactServerState\.InitialContext = (\{.*?\});', soup.decode(), re.DOTALL)
if m:
    try:
        data = json.loads(m.group(1))
        cache = data.get('ReactServerAgent.cache', {}).get('dataCache', {})
        for k, v in cache.items():
                res_text = v['res']['text']
                res_json = json.loads(res_text.split('&&')[-1])
                payload = res_json.get('payload', {})
                
                if 'aroundThisHomeSectionInfo' in k:
                    # Places (pointOfInterestList)
                    pois = payload.get('pointOfInterestList', [])
                    for poi in pois:
                        places.append({
                            "name": poi.get("name"),
                            "category": poi.get("category"),
                            "distance": poi.get("distance"),
                            "rating": poi.get("reviewRating")
                        })
                    
                    # Transit (transitData -> nearbyTransitStops)
                    transit_data = payload.get('transitData', {})
                    stops = transit_data.get('nearbyTransitStops', [])
                    for stop in stops:
                        routes = []
                        for r in stop.get('routes', []):
                            route_name = r.get('shortName') or r.get('longName')
                            if route_name and route_name not in routes:
                                routes.append(route_name)
                        transit.append({
                            "stopName": stop.get("stopName"),
                            "routes": routes
                        })
                
                # Public Records (publicRecordsInfo) (Fallback removed in favor of DOM extraction)
    except Exception:
        pass

around_this_home_data = {
    "schools": schools if schools else None,
    "places": places if places else None,
    "Transit": transit if transit else None
}

around_el = soup.find(string=lambda t: t and 'Around this home' in t)
if around_el:
    add('around_this_home', around_this_home_data, around_el.parent)
else:
    # fallback element
    add('around_this_home', around_this_home_data, soup.find('body'))

# Override status if About this home indicates pending
if 'about_this_home' in fields and 'PENDING' in fields['about_this_home']['value'].upper():
    fields['status'] = {"value": "Pending", "normalized": "Pending"}
    provenance['status'] = provenance['about_this_home']

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
for k, v in fields.items():
    print(f"{k}: {repr(v['value'])[:100]}")
