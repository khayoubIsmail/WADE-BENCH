import json
import re
from bs4 import BeautifulSoup

def get_xpath(element):
    if not element:
        return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]':
            break
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

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_DAFT.IE_001_LISTING.json'
html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_DAFT.IE_001_LISTING\page.html'

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

script = soup.find('script', id='__NEXT_DATA__')
next_data = json.loads(script.string)
listings = next_data.get('props', {}).get('pageProps', {}).get('listings', [])
ber_map = {l['listing']['title']: l['listing'].get('ber', {}).get('rating') for l in listings}

cards = soup.find_all('li', attrs={'data-testid': lambda x: x and 'result' in x})

new_records = []

for i, card in enumerate(cards):
    gold_id = f"WBV1_REAL_DAFT.IE_001_LISTING_{i+1:03d}"
    record = {
        "gold_record_id": gold_id,
        "fields": {},
        "provenance": {}
    }
    
    fields = {}
    provenance = {}

    def add_field(key, value, el, normalize_func=None, custom_tq=None, css=None):
        if not value: return
        val_str = str(value).strip() if not isinstance(value, list) else value
        if not val_str: return
        
        norm_val = val_str
        if normalize_func:
            try:
                norm_val = normalize_func(val_str)
            except:
                pass
                
        fields[key] = {
            "value": val_str,
            "normalized": norm_val
        }
        
        if el:
            provenance[key] = {
                "snapshot_id": "SNAP_REAL_DAFT.IE_001_LISTING",
                "css_selector": css,
                "xpath": get_xpath(el),
                "text_quote": custom_tq if custom_tq else (val_str[:50] if isinstance(val_str, str) else "Array of items")
            }

    a = card.find('a', href=True)
    if a:
        add_field('listing_url', "https://www.daft.ie" + a['href'], a, css='a')

    logo = card.find('img', alt='Logo')
    if logo: add_field('agent_branding_logo', logo.get('src'), logo, css='img[alt="Logo"]')

    neg_name = card.find(attrs={'data-tracking': 'agent_branding_negotiator_name'})
    if neg_name: add_field('agent_branding_negotiator_name', neg_name.text, neg_name, css='[data-tracking="agent_branding_negotiator_name"]')

    neg_img = card.find('img', alt='Negotiator Image')
    if neg_img: add_field('Negotiator_Image', neg_img.get('src'), neg_img, css='img[alt="Negotiator Image"]')

    agent_name = card.find(attrs={'data-tracking': 'agent_branding_agent_name'})
    if agent_name: add_field('agent_listing', agent_name.text, agent_name, css='[data-tracking="agent_branding_agent_name"]')

    imgs = card.find_all('img')
    prop_imgs = []
    prop_el = None
    for img in imgs:
        alt = img.get('alt', '')
        if alt and alt not in ['Logo', 'Negotiator Image'] and 'BER' not in alt:
            prop_imgs.append(img.get('src'))
            if not prop_el: prop_el = img
    if prop_imgs:
        add_field('images_urls', prop_imgs, prop_el, lambda x: prop_imgs, css='img')

    strings = []
    for el in card.find_all(string=True):
        if el.strip() and not el.parent.name in ['script', 'style']:
            strings.append((el.strip(), el.parent))

    price_idx = -1
    for idx, (txt, el) in enumerate(strings):
        if '€' in txt or '£' in txt or 'Price on Application' in txt:
            price_idx = idx
            def norm_price(p):
                p = re.sub(r'[^\d]', '', p)
                return int(p) if p else None
            add_field('price', txt, el, norm_price, css=el.name)
            break
            
    loc_txt = ""
    if price_idx > 0:
        loc_txt, loc_el = strings[price_idx - 1]
        add_field('location', loc_txt, loc_el, css=loc_el.name)
        
    for txt, el in strings:
        txt_lower = txt.lower()
        if 'bed' in txt_lower and not 'bath' in txt_lower:
            add_field('bedrooms', txt, el, lambda x: int(re.sub(r'[^\d]', '', x)), css=el.name)
        elif 'bath' in txt_lower:
            add_field('bathrooms', txt, el, lambda x: int(re.sub(r'[^\d]', '', x)), css=el.name)
        elif txt in ['Detached', 'Semi-D', 'Terraced', 'Terrace', 'End of Terrace', 'Apartment', 'Site', 'Bungalow', 'Duplex', 'Townhouse']:
            add_field('property_type', txt, el, css=el.name)
        elif 'm²' in txt_lower or ' ac' in txt_lower or 'sq ' in txt_lower or txt_lower.endswith('ac'):
            add_field('floor_area', txt, el, css=el.name)

    ber = ber_map.get(loc_txt)
    if ber:
        ber_el = card.find(attrs={'data-tracking': 'srp_ber'})
        if not ber_el:
            ber_el = card.find('svg')
        if not ber_el:
            ber_el = loc_el
        
        css_ber = '[data-tracking="srp_ber"][aria-label]' if card.find(attrs={'data-tracking': 'srp_ber'}) else None
        add_field('BER_energy_rating', f"BER {ber}", ber_el, normalize_func=lambda x: ber, custom_tq=f"BER {ber}", css=css_ber)

    record['fields'] = fields
    record['provenance'] = provenance
    new_records.append(record)

data['records'] = new_records

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Regenerated all Daft.ie JSON properties correctly with css selectors.")
