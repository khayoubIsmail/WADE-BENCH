import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_LEBONCOIN_002_DETAIL\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_LEBONCOIN_002_DETAIL.json'
SNAP_ID = "SNAP_REAL_LEBONCOIN_002_DETAIL"

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
    if el.get('data-testid'): return f"{el.name}[data-testid=\"{el['data-testid']}\"]"
    if el.get('data-qa-id'): return f"{el.name}[data-qa-id=\"{el['data-qa-id']}\"]"
    
    classes = el.get('class', [])
    stable = [c for c in classes if len(c) > 3 and not c.startswith('sc-') and c not in ('flex','col','row','grid','hidden','inline','block','relative','absolute','w-full','h-full')]
    if stable: return f"{el.name}.{stable[0].replace('!', '')}"
    
    parent = el.parent
    if parent and parent.name != '[document]':
        if parent.get('data-qa-id'):
            return f"{parent.name}[data-qa-id=\"{parent['data-qa-id']}\"] > {el.name}"
        p_classes = parent.get('class', [])
        p_stable = [c for c in p_classes if len(c) > 3 and not c.startswith('sc-') and c not in ('flex','col','row','grid','hidden','inline','block','relative','absolute','w-full','h-full')]
        if p_stable: return f"{parent.name}.{p_stable[0].replace('!', '')} > {el.name}"

    return el.name

def prov(el, val):
    val_str = val if isinstance(val, str) else str(val)
    return {
        "snapshot_id": SNAP_ID,
        "css_selector": build_css(el),
        "xpath": get_xpath(el),
        "text_quote": val_str[:80]
    }

def clean_num(text):
    text = text.replace('\u202f', '').replace('\xa0', '').replace(' ', '')
    m = re.search(r'[\d]+', text)
    return int(re.sub(r'[^\d]', '', text)) if m else None

fields = {}
provenance = {}

def add(key, val, el, norm=None):
    if val is None or val == '': return
    fields[key] = {"value": val, "normalized": norm if norm is not None else val}
    provenance[key] = prov(el, val)

# listing_url (Removed per user request)
# canon = soup.find('link', rel='canonical')
# if canon and canon.get('href'):
#     add('listing_url', canon['href'], canon)

# images_urls
imgs = soup.find_all('img', alt=lambda x: x and '(image ' in x)
if imgs:
    urls = [img['src'] for img in imgs if img.get('src')]
    add('images_urls', urls, imgs[0], urls)

# Energy
energy_el = soup.find('img', alt=lambda x: x and 'Classe énergie' in x)
if energy_el:
    add('Classe énergie', energy_el['alt'], energy_el, energy_el['alt'].replace('Classe énergie', '').strip())

ges_el = soup.find('img', alt=lambda x: x and 'GES' in x)
if ges_el:
    add('GES', ges_el['alt'], ges_el, ges_el['alt'].replace('GES', '').strip())

# Criteria
criteria_map = {
    'Type de bien': 'Type de bien',
    'Nombre de pièces': 'Nombre de pièces',
    "Nombre de salles d'eau": "Nombre de salles d'eau",
    'Type de chauffage': 'Type de chauffage',
    'Surface habitable': 'Surface habitable',
    'Nombre de chambres': 'Nombre de chambres',
    'Caractéristiques': 'Caractéristiques',
    'Mode de chauffage': 'Mode de chauffage'
}

for div in soup.find_all('div', attrs={'data-qa-id': re.compile(r'^criteria_item')}):
    texts = [t.text.strip() for t in div.find_all(['p', 'span']) if t.text.strip()]
    if len(texts) >= 2:
        label = texts[0]
        val = texts[1]
        
        if label in criteria_map:
            target_key = criteria_map[label]
            val_el = div.find_all(['p', 'span'])[-1] # Usually the last text element
            
            if target_key in ['Nombre de pièces', "Nombre de salles d'eau"]:
                add(target_key, val, val_el, clean_num(val))
            elif target_key == 'Surface habitable':
                add(target_key, val, val_el, clean_num(val))
            elif target_key == 'Nombre de chambres':
                add(target_key, val, val_el, clean_num(val))
            elif target_key == 'Caractéristiques':
                chars = [c.strip() for c in val.split(',')]
                add(target_key, chars, val_el, chars)
            else:
                add(target_key, val, val_el)

# Description
desc_el = soup.find(attrs={'data-qa-id': 'adview_description_container'})
if desc_el:
    p_el = desc_el.find('p')
    target = p_el if p_el else desc_el
    add('Description', target.text.strip(), target)

# Location
loc_el = soup.find(attrs={'data-qa-id': 'adview_location_informations'})
if loc_el:
    add('Localisation', loc_el.text.strip(), loc_el)
else:
    # Alternative location extraction
    alt_loc = soup.find('div', class_='mb-lg')
    if alt_loc:
        on_bg = alt_loc.find('div', class_='text-on-background')
        if on_bg:
            lines = [p.text.strip() for p in on_bg.find_all('p') if p.text.strip()]
            if lines:
                val = '\n'.join(lines)
                add('Localisation', val, on_bg)

# Prix du bien
price_el = soup.find(attrs={'data-qa-id': 'adview_price'})
if price_el:
    ptxt = price_el.text.strip()
    add('Prix du bien', ptxt, price_el, clean_num(ptxt))

# Prix per m2
for el in soup.find_all(lambda t: t.name in ['div','p','span'] and 'mètres carrésm²' in t.text and '€' in t.text):
    if len(el.text) < 100:
        ptxt = el.text.replace('\u202f', ' ').replace('\xa0', ' ').strip()
        m = re.search(r'([\d\s]+)€\s*par', ptxt)
        if m:
            raw_val = m.group(1).strip() + " €/m²"
            norm_val = int(re.sub(r'[^\d]', '', m.group(1)))
            add('price_per_m2', raw_val, el, norm_val)
            break

# Mensualités
for p in soup.find_all(lambda t: t.name in ['p','span'] and 'Mensualités' in t.text):
    parent = p.parent
    if parent:
        val_el = parent.find('span', class_=lambda c: c and 'text-headline-1' in c)
        if val_el:
            vtxt = val_el.text.strip()
            add('Mensualités', vtxt, val_el, clean_num(vtxt))
            break

# Vendu par & logo_agent
store_el = soup.find(attrs={'data-qa-id': 'store-contact'})
if store_el:
    name_el = store_el.find(attrs={'data-qa-id': 'pro-store-name'})
    if name_el:
        add('Vendu par', name_el.text.strip(), name_el)
    
logo_img = soup.find('img', src=lambda x: x and 'rule=bo-thumb' in x)
if logo_img:
    add('logo_agent', logo_img['src'], logo_img)

# Try to extract missing fields from __NEXT_DATA__
script_tag = soup.find('script', id='__NEXT_DATA__')
if script_tag:
    try:
        next_data = json.loads(script_tag.string)
        ad_data = next_data['props']['pageProps']['ad']
        
        if 'Localisation' not in fields:
            loc = ad_data.get('location', {})
            city_label = loc.get('city_label')
            if city_label:
                add('Localisation', city_label, script_tag)
                
        if 'Vendu par' not in fields:
            owner = ad_data.get('owner', {})
            name = owner.get('name')
            if name:
                add('Vendu par', name, script_tag)
                
        if 'logo_agent' not in fields:
            # We might find logo in attributes or other places
            store_logo = None
            add_info = ad_data.get('store', {}) if 'store' in ad_data else {}
            if 'logo' in add_info:
                add('logo_agent', add_info['logo'], script_tag)
                
        if 'Classe énergie' not in fields:
            attrs = ad_data.get('attributes', [])
            for a in attrs:
                if a.get('key') == 'energy_rate':
                    val = a.get('value_label', '')
                    add('Classe énergie', f"Classe énergie {val}", script_tag, val)
                if a.get('key') == 'ges':
                    val = a.get('value_label', '')
                    add('GES', f"GES {val}", script_tag, val)
    except Exception as e:
        print("Error parsing NEXT DATA:", e)

# Save
with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

# Use original listing_title from template if not overwritten
original_record = out_data['records'][0]
if 'listing_title' in original_record['fields']:
    fields['listing_title'] = original_record['fields']['listing_title']
    provenance['listing_title'] = original_record.get('provenance', {}).get('listing_title', {})

out_data['records'] = [{
    "gold_record_id": original_record['gold_record_id'],
    "fields": fields,
    "provenance": provenance
}]
out_data['annotation_metadata']['total_records_extracted'] = 1

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"Done. Extracted {len(fields)} fields.")
