import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_LEBONCOIN_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_LEBONCOIN_001_LISTING.json'
SNAP_ID = "SNAP_REAL_LEBONCOIN_001_LISTING"

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
    if el.get('aria-label') and el.name != 'article': return f"{el.name}[aria-label=\"{el['aria-label']}\"]"
    
    classes = el.get('class', [])
    # Find stable classes
    stable = [c for c in classes if len(c) > 3 and not c.startswith('sc-') and c not in ('flex','col','row','grid','hidden','inline','block','relative','absolute','w-full','h-full')]
    if stable: return f"{el.name}.{stable[0].replace('!', '')}" # some classes have '!' at the end like text-body-2!
    
    # Fallback to parent
    parent = el.parent
    if parent and parent.name != '[document]':
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

def clean_price(text):
    text = text.replace('\u202f', '').replace('\xa0', '').replace(' ', '')
    m = re.search(r'[\d]+', text)
    return int(re.sub(r'[^\d]', '', text)) if m else None

records = []
articles = soup.find_all('article')
real_cards = [a for a in articles if a.get('aria-label') and ('pièces' in a.get('aria-label','') or 'pièce' in a.get('aria-label','') or 'm²' in a.get('aria-label','') or 'mètres carrés' in a.get('aria-label',''))]
print(f"Found {len(real_cards)} listing cards")

for i, card in enumerate(real_cards):
    fields = {}
    provenance = {}

    def add(key, val, el, norm=None):
        if val is None or val == '': return
        fields[key] = {"value": val, "normalized": norm if norm is not None else val}
        provenance[key] = prov(el, val)

    # URL
    link_el = card.find('a', href=lambda x: x and '/ad/ventes_immobilieres/' in x)
    if link_el:
        href = link_el['href']
        if href.startswith('/'): href = 'https://www.leboncoin.fr' + href
        add('listing_url', href, link_el)
    
    # Title (Appartement · 4 pièces · 77m²)
    # It's usually in a <p> with class 'text-body-2-highlight' or we can find it by looking at the aria-label
    title_el = card.find('p', class_=lambda x: x and 'text-body-2-highlight' in x)
    if not title_el:
        # Fallback to the one matching part of aria-label
        title_el = card.find(lambda t: t.name in ['p','span'] and 'pièce' in t.text and 'm²' in t.text)
    
    if title_el:
        txt = title_el.text.strip()
        # listing_title is removed per user request
        
        parts = [p.strip() for p in txt.split('·')]
        if len(parts) > 0:
            add('property_type', parts[0], title_el)
        for p in parts[1:]:
            room_match = re.search(r'(\d+)\s*pièce', p)
            if room_match: add('rooms', p, title_el, int(room_match.group(1)))
            area_match = re.search(r'(\d+)\s*m²', p)
            if area_match: add('area', p, title_el, int(area_match.group(1)))

    # Price
    price_el = card.find('span', class_=lambda x: x and 'text-success' in x)
    if not price_el:
        price_el = card.find(lambda t: t.name in ['span','p'] and '€' in t.text and not t.find(['span','p']))
    
    if price_el:
        ptxt = price_el.text.strip()
        add('price', ptxt, price_el, clean_price(ptxt))
        
    # Price per m2
    pm2_el = card.find('div', class_=lambda x: x and 'text-caption' in x and 'text-small' in x)
    if pm2_el:
        pm2_p = pm2_el.find('p')
        target_el = pm2_p if pm2_p else pm2_el
        ptxt = target_el.text.replace('\u202f', ' ').replace('\xa0', ' ').strip()
        if '€' in ptxt and '/' in ptxt:
            # We want just the number, e.g. 5325
            m = re.search(r'([\d\s]+)€', ptxt)
            if m:
                raw_val = m.group(1).strip() + " €/m²"
                norm_val = int(re.sub(r'[^\d]', '', m.group(1)))
                add('price_per_m2', raw_val, target_el, norm_val)
    
    # Location
    loc_el = card.find('p', class_=lambda x: x and 'text-caption' in x and 'text-neutral' in x)
    if not loc_el:
        loc_el = card.find(lambda t: t.name in ['p'] and t.get('class') and 'text-caption' in t.get('class') and 'text-neutral' in t.get('class'))
    
    if loc_el:
        add('location', loc_el.text.strip(), loc_el)
        
    # Images
    img_els = card.find_all('img', src=lambda x: x and 'img.leboncoin.fr' in x)
    if img_els:
        urls = [img['src'] for img in img_els]
        add('images_urls', urls, img_els[0].parent, urls)

    # Agent Branding
    agent_el = card.find(attrs={'data-qa-id': 'pro-store-name'})
    if agent_el:
        agent_name = agent_el.text.strip()
        add('agent_branding', agent_name, agent_el)
        
    # Agent Logo
    logo_el = card.find('img', alt='Logo du professionnel')
    if logo_el and logo_el.get('src'):
        add('agent_branding_logo', logo_el['src'], logo_el)
        
    # Energy Rating
    energy_el = card.find('img', alt=lambda x: x and 'Classe énergie' in x)
    if energy_el:
        energy_alt = energy_el['alt']
        normalized = energy_alt.replace('Classe énergie', '').strip()
        add('energy_rating', energy_alt, energy_el, normalized)
        
    # Additional Facilities
    facilities = []
    facility_els = [s for s in card.find_all('span') if s.get('class') == ['text-body-2']]
    for fel in facility_els:
        ftxt = fel.text.strip()
        if ftxt: facilities.append(ftxt)
    if facilities:
        add('additional_facilities', facilities, facility_els[0], facilities)

    record_id = f"WBV1_REAL_LEBONCOIN_001_LISTING_{str(i+1).zfill(3)}"
    records.append({
        "gold_record_id": record_id,
        "fields": fields,
        "provenance": provenance
    })

with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

out_data['records'] = records
out_data['annotation_metadata']['total_records_extracted'] = len(records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"Done. Wrote {len(records)} records.")
