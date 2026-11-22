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
    if not el: return { "snapshot_id": "SNAP_REAL_RIGHTMOVE_002_DETAIL", "css_selector": None, "xpath": None, "text_quote": None }
    return {
        "snapshot_id": "SNAP_REAL_RIGHTMOVE_002_DETAIL",
        "css_selector": get_css_selector(el),
        "xpath": get_xpath(el),
        "text_quote": text if text else None
    }

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_RIGHTMOVE_002_DETAIL\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_RIGHTMOVE_002_DETAIL.json'

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

record = {}
prov = {}

# images_urls
imgs = soup.find_all('img')
img_urls = []
first_img_el = None
for img in imgs:
    src = img.get('src', '')
    if 'dir/crop' in src or 'property-photo' in src:
        img_urls.append(src)
        if not first_img_el: first_img_el = img
if img_urls:
    record['images_urls'] = {'value': img_urls}
    prov['images_urls'] = build_prov(first_img_el)

# location
addr_el = soup.find('h1')
if addr_el:
    text = addr_el.get_text(strip=True)
    text = re.sub(r'^.*for rent in\s*', '', text) # strip prefix if needed
    record['location'] = {'value': text}
    prov['location'] = build_prov(addr_el, text[:30])

# listing_url
canon = soup.find('link', rel='canonical')
if canon and canon.get('href'):
    record['listing_url'] = {'value': canon['href']}
    prov['listing_url'] = build_prov(canon)

# rating and review_count
rvs_block = soup.find(class_=re.compile('rvsRatingsBlock'))
if rvs_block:
    rvs_text = rvs_block.get_text(strip=True)
    m1 = re.search(r'rated ([\d\.]+) out of', rvs_text)
    if m1:
        record['rating'] = {'value': m1.group(1)}
        prov['rating'] = build_prov(rvs_block, m1.group(1))

rvs2 = soup.find(string=re.compile('total reviews', re.IGNORECASE))
if rvs2:
    parent_text = rvs2.parent.get_text()
    m2 = re.search(r'(\d+) total reviews', parent_text, re.IGNORECASE)
    if m2:
        record['review_count'] = {'value': m2.group(1)}
        prov['review_count'] = build_prov(rvs2.parent, m2.group(1))

# price
price_el = soup.find('div', string=re.compile('£'))
if price_el:
    record['price'] = {'value': price_el.get_text(strip=True)}
    prov['price'] = build_prov(price_el, record['price']['value'][:30])

# published date
pub_date_el = soup.find('div', string=re.compile('Added on'))
if pub_date_el:
    raw_date = pub_date_el.get_text(strip=True)
    clean_date = re.sub(r'^(Added on |Reduced on |Added )', '', raw_date, flags=re.IGNORECASE)
    record['published date'] = {'value': clean_date}
    prov['published date'] = build_prov(pub_date_el, clean_date[:30])

# agent_branding_name
agent_container = soup.find(string=re.compile('Marketed by', re.IGNORECASE))
if agent_container and agent_container.parent:
    branch_name_el = agent_container.parent.parent.find('div', attrs={'data-testid': 'branchName'})
    if branch_name_el:
        record['agent_branding_name'] = {'value': branch_name_el.get_text(strip=True)}
        prov['agent_branding_name'] = build_prov(branch_name_el, record['agent_branding_name']['value'][:30])

# agent_branding_logo
agent_logo = soup.find('img', alt=re.compile('logo', re.IGNORECASE))
if agent_logo and agent_logo.get('src'):
    record['agent_branding_logo'] = {'value': agent_logo['src']}
    prov['agent_branding_logo'] = build_prov(agent_logo)

# agent_branding_location
if agent_container and agent_container.parent:
    branch_name_el = agent_container.parent.parent.find('div', attrs={'data-testid': 'branchName'})
    if branch_name_el:
        loc_el = branch_name_el.find_next_sibling('div')
        if loc_el and loc_el.get('title'):
            record['agent_branding_location'] = {'value': loc_el['title'].strip().replace('\n', ', ')}
            prov['agent_branding_location'] = build_prov(loc_el)

# Detail keys
for label in ['Furnish type', 'PROPERTY TYPE', 'BEDROOMS', 'BATHROOMS', 'PARKING']:
    dd = None
    for dt in soup.find_all('dt'):
        if label.lower() in dt.get_text().lower():
            dd = dt.find_next_sibling('dd')
            break
    if dd:
        record[label] = {'value': dd.get_text(strip=True)}
        prov[label] = build_prov(dd, record[label]['value'][:30])

# Key features
kf_h2 = soup.find('h2', string=re.compile('Key features', re.IGNORECASE))
if kf_h2:
    ul = kf_h2.find_next_sibling('ul')
    if ul:
        feats = [li.get_text(strip=True) for li in ul.find_all('li')]
        record['Key features'] = {'value': feats}
        prov['Key features'] = build_prov(ul)

# Description
desc_h2 = soup.find('h2', string=re.compile('^Description$', re.IGNORECASE))
if desc_h2:
    desc_div = desc_h2.find_next_sibling('div')
    if desc_div:
        record['Description'] = {'value': desc_div.get_text('\n', strip=True)}
        prov['Description'] = build_prov(desc_div, record['Description']['value'][:30])

# first review
first_review = soup.find('li', class_=re.compile('rvsReviewCard'))
if first_review:
    fr_val = {}
    
    r_el = first_review.find(string=re.compile('rated \d\.\d'))
    if r_el:
        m = re.search(r'rated (\d\.\d)', r_el)
        if m: fr_val['rating'] = m.group(1)
        
    auth_el = first_review.find('p', class_='rvsAuthor')
    if auth_el:
        b = auth_el.find('b')
        if b: fr_val['person_name'] = b.get_text(strip=True)
            
    date_el = first_review.find('p', class_='rvsCreatedDate')
    if date_el: fr_val['date review'] = date_el.get_text(strip=True)
        
    title_el = first_review.find('p', class_='rvsMainQuestion')
    if title_el: fr_val['title'] = title_el.get_text(strip=True)
        
    p_texts = first_review.find_all('p', class_='rvsReviewText')
    if p_texts:
        fr_val['review_content'] = ' '.join(p.get_text(strip=True) for p in p_texts)
        
    record['first review'] = {'value': fr_val, 'normalized': dict(fr_val)}
    prov['first review'] = build_prov(first_review)

# Add normalized
for k in list(record.keys()):
    if k != 'first review':
        record[k]['normalized'] = record[k]['value']

# ISO date format for published date
if 'published date' in record:
    val = record['published date']['value']
    m_date = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', val)
    if m_date:
        record['published date']['normalized'] = f"{m_date.group(3)}-{m_date.group(2)}-{m_date.group(1)}"

# ISO date format for review date
if 'first review' in record and 'date review' in record['first review']['value']:
    val = record['first review']['value']['date review']
    import datetime
    try:
        dt = datetime.datetime.strptime(val, "%B %Y")
        record['first review']['normalized']['date review'] = dt.strftime("%Y-%m")
    except ValueError:
        pass

out_records = [{
    'gold_record_id': 'WBV1_REAL_RIGHTMOVE_002_DETAIL_001',
    'fields': record,
    'provenance': prov,
    'notes': 'Extracted via script'
}]

with open(json_path, 'r', encoding='utf-8') as f:
    gold_data = json.load(f)

gold_data['records'] = out_records
gold_data['annotation_metadata']['total_records_extracted'] = len(out_records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(gold_data, f, indent=2, ensure_ascii=False)

print('Updated JSON file.')
