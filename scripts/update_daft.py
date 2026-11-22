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

cards = soup.find_all('li', attrs={'data-testid': lambda x: x and 'result' in x})
print(f"Found {len(cards)} cards.")

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

    def add_field(key, value, el, normalize_func=None):
        if not value: return
        val_str = str(value).strip()
        if not val_str: return
        
        norm_val = val_str
        if normalize_func:
            try:
                norm_val = normalize_func(val_str)
            except:
                pass
                
        fields[key] = {
            "value": val_str if not isinstance(value, list) else value,
            "normalized": norm_val if not isinstance(norm_val, list) else norm_val
        }
        
        if el:
            # We don't have css_selector easily, so just store xpath and text
            provenance[key] = {
                "snapshot_id": "SNAP_REAL_DAFT.IE_001_LISTING",
                "xpath": get_xpath(el),
                "text_quote": val_str[:50] if not isinstance(value, list) else "Array of items"
            }

    # listing url
    a = card.find('a', href=True)
    if a:
        url = "https://www.daft.ie" + a['href']
        add_field('listing_url', url, a)

    # agent_branding_logo
    logo = card.find('img', alt='Logo')
    if logo: add_field('agent_branding_logo', logo.get('src'), logo)

    # agent_branding_negotiator_name
    neg_name = card.find(attrs={'data-tracking': 'agent_branding_negotiator_name'})
    if neg_name: add_field('agent_branding_negotiator_name', neg_name.text, neg_name)

    # Negotiator_Image
    neg_img = card.find('img', alt='Negotiator Image')
    if neg_img: add_field('Negotiator_Image', neg_img.get('src'), neg_img)

    # agent_listing
    agent_name = card.find(attrs={'data-tracking': 'agent_branding_agent_name'})
    if agent_name: add_field('agent_listing', agent_name.text, agent_name)

    # images_urls
    imgs = card.find_all('img')
    prop_imgs = []
    prop_el = None
    for img in imgs:
        alt = img.get('alt', '')
        if alt and alt not in ['Logo', 'Negotiator Image'] and 'BER' not in alt:
            prop_imgs.append(img.get('src'))
            if not prop_el: prop_el = img
    if prop_imgs:
        add_field('images_urls', prop_imgs, prop_el, lambda x: prop_imgs)

    # Search for specific strings in text nodes
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
            add_field('price', txt, el, norm_price)
            break
            
    if price_idx > 0:
        loc_txt, loc_el = strings[price_idx - 1]
        add_field('location', loc_txt, loc_el)
        
    for txt, el in strings:
        if 'Bed' in txt:
            add_field('bedrooms', txt, el, lambda x: int(re.sub(r'[^\d]', '', x)))
        elif 'Bath' in txt:
            add_field('bathrooms', txt, el, lambda x: int(re.sub(r'[^\d]', '', x)))
        elif 'm²' in txt or 'ac' in txt or 'sq' in txt:
            add_field('floor_area', txt, el)
        elif txt in ['Detached', 'Semi-D', 'Terraced', 'End of Terrace', 'Apartment', 'Site', 'Bungalow', 'Duplex']:
            add_field('property_type', txt, el)

    # BER
    ber_img = card.find('img', alt=lambda x: x and 'BER' in x)
    if ber_img:
        add_field('ber_energy_rating', ber_img.get('alt'), ber_img)

    record['fields'] = fields
    record['provenance'] = provenance
    new_records.append(record)

data['records'] = new_records
data['annotation_metadata']['total_records_extracted'] = len(new_records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated daft.ie json successfully with", len(new_records), "records.")
