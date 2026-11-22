import json
import re
from bs4 import BeautifulSoup
import os

def get_css_selector(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.get('id'):
            path.insert(0, el.name + '#' + el['id'])
            break
        else:
            siblings = el.find_previous_siblings(el.name)
            nth = len(siblings) + 1
            if nth > 1 or el.find_next_siblings(el.name):
                path.insert(0, f'{el.name}:nth-of-type({nth})')
            else:
                path.insert(0, el.name)
        el = el.parent
    return ' > '.join(path) if path else None

def get_xpath(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.name == 'html':
            path.insert(0, '/html')
            break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        path.insert(0, f'{el.name}[{nth}]')
        el = el.parent
    return '/' + '/'.join(path) if path else None

def build_prov(el, text=None):
    if not el: return { "snapshot_id": "SNAP_REAL_RIGHTMOVE_001_LISTING", "css_selector": None, "xpath": None, "text_quote": None }
    return {
        "snapshot_id": "SNAP_REAL_RIGHTMOVE_001_LISTING",
        "css_selector": get_css_selector(el),
        "xpath": get_xpath(el),
        "text_quote": text if text else None
    }

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_RIGHTMOVE_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_RIGHTMOVE_001_LISTING.json'

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

cards = soup.find_all('div', class_=re.compile('PropertyCard_propertyCardContainerWrapper'))
if not cards:
    cards = soup.find_all('div', class_=re.compile('propertyCard'))

out_records = []
for i, card in enumerate(cards):
    record = {}
    prov = {}
    
    # listing_url
    a = card.find('a', href=re.compile(r'/properties/\d+'))
    if a:
        record['listing_url'] = {'value': 'https://www.rightmove.co.uk' + a['href']}
        prov['listing_url'] = build_prov(a)
    
    # images_urls
    imgs = card.find_all('img')
    img_urls = []
    first_img_el = None
    for img in imgs:
        src = img.get('src', '')
        if 'dir/crop/' in src or 'property-photo' in src:
            img_urls.append(src)
            if not first_img_el: first_img_el = img
    if img_urls:
        record['images_urls'] = {'value': img_urls}
        prov['images_urls'] = build_prov(first_img_el)
        
    # location
    addr = card.find('address')
    if addr:
        record['location'] = {'value': addr.get_text(strip=True)}
        prov['location'] = build_prov(addr, record['location']['value'][:30])
        
    # type
    typ = card.find(['h2', 'span'], class_=re.compile('title|type', re.IGNORECASE))
    if typ:
        record['type'] = {'value': typ.get_text(strip=True)}
        prov['type'] = build_prov(typ, record['type']['value'][:30])
        
    # description
    desc = card.find('p', attrs={'data-testid': 'property-description'})
    if desc:
        record['description'] = {'value': desc.get_text(strip=True)}
        prov['description'] = build_prov(desc, record['description']['value'][:30])
        
    # listed_by
    agent_link = card.find('a', href=re.compile('/estate-agents/'))
    if agent_link and agent_link.get('title'):
        record['listed_by'] = {'value': agent_link['title']}
        prov['listed_by'] = build_prov(agent_link, agent_link['title'][:30])
    elif card.find('span', class_=re.compile('MarketedBy_joinedText')):
        span_el = card.find('span', class_=re.compile('MarketedBy_joinedText'))
        m = span_el.get_text(strip=True)
        m = re.sub(r'^(Added.*?by\s+)', '', m)
        record['listed_by'] = {'value': m}
        prov['listed_by'] = build_prov(span_el, m[:30])
        
    # agent_branding_logo
    logo = card.find('img', class_=re.compile('EstateAgent_estateAgentLogo'))
    if logo and logo.get('src'):
        record['agent_branding_logo'] = {'value': logo['src']}
        prov['agent_branding_logo'] = build_prov(logo)
        
    # agent_branding_phone
    phone = card.find('a', attrs={'data-testid': 'contact-agent-phone-number'})
    if phone and phone.get('href'):
        val = phone['href'].replace('tel:', '').strip()
        record['agent_branding_phone'] = {'value': val}
        prov['agent_branding_phone'] = build_prov(phone)
        
    # published_date
    pub_date = card.find('span', class_=re.compile('MarketedBy_addedOrReduced'))
    if pub_date and pub_date.get_text(strip=True):
        raw_date = pub_date.get_text(strip=True)
        clean_date = re.sub(r'^(Added on |Reduced on |Added )', '', raw_date, flags=re.IGNORECASE)
        record['published_date'] = {'value': clean_date}
        prov['published_date'] = build_prov(pub_date, clean_date[:30])
        
    # beedrooms
    bed = card.find('div', class_=lambda c: c and 'bedContainer' in c)
    if bed:
        record['beedrooms'] = {'value': bed.get_text(strip=True)}
        prov['beedrooms'] = build_prov(bed, record['beedrooms']['value'][:30])
        
    # bathrooms
    bath = card.find('div', class_=lambda c: c and 'bathContainer' in c)
    if bath:
        record['bathrooms'] = {'value': bath.get_text(strip=True)}
        prov['bathrooms'] = build_prov(bath, record['bathrooms']['value'][:30])
        
    # price
    prc = card.find('div', class_=lambda c: c and c.startswith('PropertyPrice_price__'))
    if not prc:
        prc = card.find('div', string=re.compile('£'))
    if prc:
        record['price'] = {'value': prc.get_text(strip=True)}
        prov['price'] = build_prov(prc, record['price']['value'][:30])
        
    for k in list(record.keys()):
        record[k]['normalized'] = record[k]['value']

    if 'published_date' in record:
        val = record['published_date']['value']
        m_date = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', val)
        if m_date:
            record['published_date']['normalized'] = f"{m_date.group(3)}-{m_date.group(2)}-{m_date.group(1)}"

    if 'listing_url' in record:
        out_records.append({
            'gold_record_id': f'WBV1_REAL_RIGHTMOVE_001_LISTING_{i+1:03d}',
            'fields': record,
            'provenance': prov,
            'notes': 'Extracted via script'
        })

print(f'Extracted {len(out_records)} records.')

with open(json_path, 'r', encoding='utf-8') as f:
    gold_data = json.load(f)

gold_data['records'] = out_records
gold_data['annotation_metadata']['total_records_extracted'] = len(out_records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(gold_data, f, indent=2, ensure_ascii=False)

print('Updated JSON file.')
