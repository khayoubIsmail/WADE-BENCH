import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_DAFT.IE_002_DETAIL\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_DAFT.IE_002_DETAIL.json'

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

def get_xpath(element):
    if not element: return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]': break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1: components.append(child.name)
        else:
            try:
                index = siblings.index(child) + 1
                components.append(f"{child.name}[{index}]")
            except ValueError:
                components.append(child.name)
        child = parent
    components.reverse()
    return f"/{'/'.join(components)}"

def build_css_selector(el):
    if not el: return ""
    def get_stable_attr(node):
        if not node or not hasattr(node, 'get'): return None
        if node.get('itemprop'): return f'{node.name}[itemprop="{node.get("itemprop")}"]'
        if node.get('data-tracking'): return f'{node.name}[data-tracking="{node.get("data-tracking")}"]'
        if node.get('data-testid'): return f'{node.name}[data-testid="{node.get("data-testid")}"]'
        node_id = node.get('id')
        if node_id and isinstance(node_id, str): 
            if len(node_id) < 30 and not re.search(r'\d{6}', node_id): return f'{node.name}#{node_id}'
        classes = node.get('class', [])
        if isinstance(classes, str): classes = classes.split()
        valid_classes = [c for c in classes if len(c) > 2 and not c.startswith('sc-') and c not in ['flex', 'col', 'row', 'container', 'wrapper', 'item', 'list']]
        if valid_classes: return f'{node.name}.{valid_classes[0]}'
        return None

    path = []
    curr = el
    while curr and curr.name not in ['body', 'html', '[document]']:
        attr = get_stable_attr(curr)
        if attr:
            if path: return f"{attr} > " + " > ".join(path[::-1])
            else: return attr
        siblings = curr.find_previous_siblings(curr.name)
        if siblings: path.append(f"{curr.name}:nth-of-type({len(siblings) + 1})")
        else: path.append(curr.name)
        curr = curr.parent
    if path: return " > ".join(path[::-1])
    return el.name if el.name else ""

def find_by_text(text, partial=False):
    if partial:
        for el in soup.find_all(string=lambda t: t and text in t):
            if el.strip(): return el.parent
    else:
        for el in soup.find_all(string=lambda t: t and t.strip() == text):
            return el.parent
    return None

fields = {}
provenance = {}

def get_prov(el, val):
    val_str = str(val).strip() if not isinstance(val, list) else val
    return {
        "snapshot_id": "SNAP_REAL_DAFT.IE_002_DETAIL",
        "css_selector": build_css_selector(el),
        "xpath": get_xpath(el),
        "text_quote": val_str[:50] if isinstance(val_str, str) else "Array of items"
    }

def add_flat_field(key, val, el, norm=None):
    if not val or not el: return
    val_str = str(val).strip() if not isinstance(val, list) else val
    fields[key] = {"value": val_str, "normalized": norm if norm is not None else val_str}
    provenance[key] = get_prov(el, val_str)

# 1. Overview Fields
loc_el = soup.find('h1', attrs={'data-testid': 'address'})
if loc_el: add_flat_field('location', loc_el.text.strip(), loc_el)

price_el = soup.find('h2', attrs={'data-testid': 'price'})
if price_el: add_flat_field('price', price_el.text.strip(), price_el, int(re.sub(r'[^\d]', '', price_el.text)))

beds_el = soup.find(attrs={'data-testid': 'beds'})
if beds_el: add_flat_field('bedrooms', beds_el.text.strip(), beds_el, int(re.sub(r'[^\d]', '', beds_el.text)))

baths_el = soup.find(attrs={'data-testid': 'baths'})
if baths_el: add_flat_field('bathrooms', baths_el.text.strip(), baths_el, int(re.sub(r'[^\d]', '', baths_el.text)))

area_el = soup.find(attrs={'data-testid': 'floor-area'})
if area_el: add_flat_field('floor_area', area_el.text.strip(), area_el)

type_el = soup.find(attrs={'data-testid': 'property-type'})
if type_el: add_flat_field('type', type_el.text.strip(), type_el)

script = soup.find('script', id='__NEXT_DATA__')
data_nxt = json.loads(script.string) if script else {}
props = data_nxt.get('props', {}).get('pageProps', {}).get('listing', {})

ber_svg_title = soup.find('title', string=lambda t: t and 'ber_' in t)
ber_svg = ber_svg_title.parent if ber_svg_title else soup.find('svg')
if data_nxt and 'props' in data_nxt:
    ber_val = props.get('ber', {}).get('rating', '')
    if ber_val:
        add_flat_field('BER_energy_rating', f"BER {ber_val}", ber_svg, ber_val)
    if ber_val:
        add_flat_field('BER_energy_rating', f"BER {ber_val}", ber_svg, ber_val)

gallery = soup.find(attrs={'data-testid': 'gallery'}) or soup.find(attrs={'data-testid': 'carousel'})
if gallery:
    imgs = [img['src'] for img in gallery.find_all('img') if 'BER' not in img.get('alt', '')]
    if imgs: add_flat_field('images_urls', imgs, gallery)

# Use NEXT_DATA for exact listing_url if present
listing_url = "https://www.daft.ie" + props.get('seoFriendlyPath', '')
share_btn = soup.find('button', attrs={'aria-label': 'Share'}) or loc_el
add_flat_field('listing_url', listing_url, share_btn)

# Agent
logo_el = soup.find('img', alt=lambda x: x and 'Logo' in x)
if logo_el: add_flat_field('agent_branding_logo', logo_el['src'], logo_el)

neg_name_el = soup.find(attrs={'data-testid': 'negotiator-name'})
if neg_name_el: add_flat_field('negotiator_name', neg_name_el.text.strip(), neg_name_el)

neg_img = soup.find('img', alt='Negotiator Image')
if neg_img: add_flat_field('Negotiator_Image', neg_img['src'], neg_img)

# Details
for p in ['Price per m²', 'Estimated Stamp Duty', 'Selling Type', 'BER No', 'Energy Performance']:
    label_el = find_by_text(p)
    if label_el:
        val_el = label_el.find_next_sibling()
        if not val_el: val_el = label_el.parent.find_all()[-1]
        if val_el: add_flat_field(p.replace(' ', '_'), val_el.text.strip(), val_el)

# Nested: About 14 Riverwood Place
about_f = {}
about_p = {}
h_label = find_by_text("Highlights")
if h_label:
    ul = h_label.find_next('ul')
    if ul:
        h_vals = [li.text.strip() for li in ul.find_all('li')]
        about_f['Highlights'] = {"value": h_vals, "normalized": h_vals}
        about_p['Highlights'] = get_prov(ul, h_vals)

d_label = find_by_text("Description")
if d_label:
    desc_el = soup.find(attrs={'data-testid': 'description'})
    if desc_el:
        about_f['Description'] = {"value": desc_el.text.strip(), "normalized": desc_el.text.strip()}
        about_p['Description'] = get_prov(desc_el, desc_el.text.strip())

local_f = {}
local_p = {}
for view, testid in [("Satellite View", "satelite-button"), ("Street View", "streetview-button")]:
    v_el = soup.find('a', attrs={'data-testid': testid})
    if v_el and v_el.get('href'):
        href = v_el['href']
        local_f[view.replace(' ', '_')] = {"value": href, "normalized": href}
        local_p[view.replace(' ', '_')] = get_prov(v_el, href)

if local_f:
    about_f['The_local_area_of_14_Riverwood_Place'] = local_f
    about_p['The_local_area_of_14_Riverwood_Place'] = local_p

if about_f:
    fields['About_14_Riverwood_Place'] = about_f
    provenance['About_14_Riverwood_Place'] = about_p

# Nested: Local schools and transport
schools_f = {}
schools_p = {}
for t, testid in [("Primary Schools", "tabpanel-0"), ("Secondary Schools", "tabpanel-1"), ("Public Transport", "tabpanel-2")]:
    panel = soup.find(id=testid)
    
    if panel:
        rows = []
        tables = panel.find_all('table')
        for table in tables:
            for tr in table.find_all('tr'):
                row_dict = {}
                ths = tr.find_all('th', attrs={'data-table-heading-mobile-id': True})
                tds = tr.find_all('td')
                if ths and tds and len(ths) == len(tds):
                    for th, td in zip(ths, tds):
                        row_dict[th.text.strip()] = td.text.strip()
                    rows.append(row_dict)
                    
        if not rows:
            schools_f[t.replace(' ', '_')] = {"value": None, "normalized": None}
            schools_p[t.replace(' ', '_')] = get_prov(panel, "")
        else:
            schools_f[t.replace(' ', '_')] = {"value": rows, "normalized": rows}
            schools_p[t.replace(' ', '_')] = get_prov(panel, rows)
    else:
        # Tab not visible or doesn't exist
        schools_f[t.replace(' ', '_')] = {"value": None, "normalized": None}
        schools_p[t.replace(' ', '_')] = {"snapshot_id": "SNAP_REAL_DAFT.IE_002_DETAIL", "css_selector": "", "xpath": "", "text_quote": ""}

if schools_f:
    fields['Local_schools_and_transport'] = schools_f
    provenance['Local_schools_and_transport'] = schools_p

# Nested: BER Details
ber_f = {}
ber_p = {}
ber_det_label = find_by_text("BER Details")
if ber_det_label:
    ber_parent = ber_det_label.find_next_sibling()
    if ber_parent:
        rating_el = ber_parent.find('img', alt=lambda x: x and 'BER' in x.upper())
        if rating_el:
            ber_f['rating'] = {"value": rating_el['alt'], "normalized": rating_el['alt']}
            ber_p['rating'] = get_prov(rating_el, rating_el['alt'])
        
        bno_el = ber_parent.find(string=lambda t: t and 'BER No' in t)
        if bno_el:
            v_el = bno_el.parent.find_next_sibling()
            if v_el:
                ber_f['BER_No'] = {"value": v_el.text.strip(), "normalized": v_el.text.strip()}
                ber_p['BER_No'] = get_prov(v_el, v_el.text.strip())
        
        epi_el = ber_parent.find(string=lambda t: t and 'Energy Performance Indicator' in t)
        if epi_el:
            v_el = epi_el.parent.find_next_sibling()
            if v_el:
                ber_f['Energy_Performance_Indicator'] = {"value": v_el.text.strip(), "normalized": v_el.text.strip()}
                ber_p['Energy_Performance_Indicator'] = get_prov(v_el, v_el.text.strip())
if ber_f:
    fields['BER_Details'] = ber_f
    provenance['BER_Details'] = ber_p

# Date and Views
date_el = find_by_text("Date listed")
if date_el:
    dv = date_el.find_next_sibling()
    if dv: add_flat_field('Date_listed', dv.text.strip(), dv)

views_el = find_by_text("Views")
if views_el:
    vv = views_el.find_next_sibling()
    if vv: add_flat_field('Views', vv.text.strip(), vv, int(re.sub(r'[^\d]', '', vv.text)))

with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

out_data['records'] = [{
    "gold_record_id": "WBV1_REAL_DAFT.IE_002_DETAIL_001",
    "fields": fields,
    "provenance": provenance
}]

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print("Done extracting DAFT detail nested.")
