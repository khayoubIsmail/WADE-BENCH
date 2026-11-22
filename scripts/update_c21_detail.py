import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_CENTURY_21_002_DETAIL\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_002_DETAIL.json'

with open(html_path, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

fields = {}
provenance = {}

def add_field(key, value, selector):
    if not value: return
    val_str = str(value).strip()
    
    # Try normalization for specific fields
    norm_val = val_str
    if key in ['price', 'Price', 'Monthly_HOA_dues', 'Price_per_sq._ft.']:
        try:
            norm_val = float(val_str.replace('$', '').replace(',', '').strip())
            if norm_val.is_integer(): norm_val = int(norm_val)
        except: pass
    elif key in ['Beds', 'Baths', 'Bedrooms', 'Total_bathrooms', 'Full_bathrooms', 'Garage_spaces', 'Year_built']:
        try:
            norm_val = int(val_str.split()[0].replace(',', ''))
        except: pass
    elif key in ['Flooring', 'Kitchen_Description', 'Heating', 'Appliances', 'Amenities']:
        norm_val = [x.strip() for x in val_str.split(',')]
    
    fields[key] = {
        "value": val_str,
        "normalized": norm_val
    }
    provenance[key] = {
        "snapshot_id": "SNAP_REAL_CENTURY_21_002_DETAIL",
        "css_selector": selector,
        "text_quote": val_str[:50]
    }

# Top-level fields
# listing_url
link = soup.find('link', rel='canonical')
if link:
    add_field('listing_url', link.get('href'), 'link[rel="canonical"]')

# image_url
img = soup.find('meta', property='og:image')
if img:
    add_field('image_url', img.get('content'), 'meta[property="og:image"]')
    
# Title / Location
loc = soup.find('h1', class_='property-address') or soup.find('div', class_='property-address')
if not loc:
    loc = soup.find(string=lambda s: s and 'Foster City, CA' in s)
if loc:
    add_field('Location', loc.text if hasattr(loc, 'text') else str(loc), 'h1')

# listed by / Office
office = soup.find(string=lambda s: s and 'Listed by' in s)
if office:
    text = office.strip()
    if 'Listed by' in text:
        text = text.replace('Listed by:', '').replace('Listed by', '').strip()
    add_field('listed_by', text, 'div:contains("Listed by")')
    add_field('Office', text, 'div:contains("Listed by")')

# About this home
about = soup.find('div', class_='property-description')
if about:
    add_field('About_this_home', about.text, '.property-description')

# We'll collect all facts from li tags
lis = soup.find_all('li')
for li in lis:
    text = li.get_text(separator='|', strip=True)
    if '|:|' in text:
        k, v = text.split('|:|', 1)
        k = k.strip().replace(' ', '_').replace('.', '._')
        v = v.strip()
        if k == 'Price_per_sq._ft.': k = 'Price_per_sq._ft.'
        add_field(k, v, 'li')
    elif '|' not in text and ':' in text:
        k, v = text.split(':', 1)
        k = k.strip().replace(' ', '_')
        v = v.strip()
        add_field(k, v, 'li')
    else:
        # Check for simple properties like "4 Beds"
        if ' Beds' in text: add_field('Beds', text.replace('Beds', '').strip(), 'li')
        elif ' Baths' in text: add_field('Baths', text.replace('Baths', '').strip(), 'li')
        elif ' sq. ft.' in text and 'Price' not in text and 'Living' not in text and 'Building' not in text: 
            add_field('sq._ft.', text.replace('sq. ft.', '').strip(), 'li')
        elif 'Single family' in text or 'Condo' in text or 'Townhouse' in text:
            add_field('type', text, 'li')
        elif text.lower() in ['active', 'pending', 'sold', 'contingent']:
            add_field('status', text, 'li')
            
# Find price directly if not in facts
if 'Price' not in fields:
    price = soup.find(string=lambda s: s and s.strip().startswith('$') and not 'Price' in s)
    if price: add_field('price', price.strip(), 'div')

data['records'][0]['fields'] = fields
data['records'][0]['provenance'] = provenance

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Added all fields successfully. Field count:", len(fields))
