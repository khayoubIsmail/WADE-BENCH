"""
add_listing_url_apartments.py
Extracts listing_url from page.html and injects it into each record
of WBV1_REAL_APARTMENTS_001_LISTING.json by matching address order.
"""

import json
import re
from bs4 import BeautifulSoup


def get_css_selector_absolute(el):
    """Build absolute CSS nth-of-type chain from element to root."""
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.get('id'):
            path.insert(0, el.name + '#' + el['id'])
            break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        if nth > 1 or el.find_next_siblings(el.name):
            path.insert(0, '%s:nth-of-type(%d)' % (el.name, nth))
        else:
            path.insert(0, el.name)
        el = el.parent
    return ' > '.join(path) if path else None


def get_xpath_absolute(el):
    """Build absolute XPath from element to root."""
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.name == 'html':
            path.insert(0, '/html')
            break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        path.insert(0, '%s[%d]' % (el.name, nth))
        el = el.parent
    return '/' + '/'.join(path) if path else None

BASE_URL = 'https://www.coldwellbankerhomes.com'
SNAP_ID = 'SNAP_REAL_APARTMENTS_001_LISTING'

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_APARTMENTS_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_001_LISTING.json'

with open(html_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Extract listing URLs in DOM order via h2.address-price-heading -> parent <a>
listings = []
for h2 in soup.find_all('h2', class_='address-price-heading'):
    a = h2.find_parent('a')
    if a and a.get('href'):
        href = a['href']
        full_url = BASE_URL + href if href.startswith('/') else href
        addr_text = h2.get_text(' ', strip=True)
        listings.append({'url': full_url, 'address': addr_text, 'element': a})

print('Found %d listing URLs in HTML' % len(listings))

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data.get('records', [])

if len(listings) != len(records):
    print('WARNING: count mismatch — %d URLs vs %d records' % (len(listings), len(records)))

for i, rec in enumerate(records):
    if i >= len(listings):
        break

    listing = listings[i]
    url = listing['url']

    # Add listing_url field (insert at front)
    fields = rec.get('fields', {})
    new_fields = {'listing_url': {'value': url, 'normalized': url}}
    new_fields.update(fields)
    rec['fields'] = new_fields

    # Add provenance for listing_url
    prov = rec.get('provenance', {})
    a_el = listing['element']

    # CSS selector
    css = "a[href*='%s']" % listing['url'].replace(BASE_URL, '')

    # Stable xpath from href fragment
    pid_m = re.search(r'pid_(\d+)', url)
    xpath = "//a[contains(@href,'%s')]" % (pid_m.group(0) if pid_m else listing['url'].replace(BASE_URL, ''))

    css_abs = get_css_selector_absolute(a_el)
    xpath_abs = get_xpath_absolute(a_el)

    new_listing_url_prov = {
        'snapshot_id': SNAP_ID,
        'css_selector': css,
        'css_selector_absolute': css_abs,
        'xpath': xpath,
        'xpath_absolute': xpath_abs,
        'attribute': 'href',
        'text_quote': None
    }

    # Build provenance: keep existing entries but always overwrite listing_url
    prov = {k: v for k, v in rec.get('provenance', {}).items() if k != 'listing_url'}
    prov = {'listing_url': new_listing_url_prov, **prov}
    rec['provenance'] = prov

data['records'] = records

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Done. Sample:')
print(json.dumps(records[0]['fields']['listing_url'], indent=2))
