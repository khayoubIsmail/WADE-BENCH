import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_CENTURY_21_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_001_LISTING.json'

with open(html_path, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

cards = soup.select('li.container-card')
print(f"Found {len(cards)} cards in HTML.")

new_records = []

for i, card in enumerate(cards):
    gold_id = f"WBV1_REAL_CENTURY_21_001_LISTING_{i+1:03d}"
    record = {
        "gold_record_id": gold_id,
        "fields": {},
        "provenance": {}
    }
    
    fields = {}
    provenance = {}

    def add_field(key, value, selector):
        if value:
            val_str = value.strip()
            fields[key] = {
                "value": val_str,
                "normalized": val_str
            }
            provenance[key] = {
                "snapshot_id": "SNAP_REAL_CENTURY_21_001_LISTING",
                "css_selector": selector,
                "text_quote": val_str[:50]  # Just a snippet
            }

    # Open House time
    open_house = card.find('span', class_='info-badge', string=lambda s: s and 'Open' in s)
    if open_house:
        add_field('Open_House_time', open_house.text, '.info-badge')

    # image
    img = card.find('img', class_='property-img')
    if img and img.get('src'):
        add_field('image', img.get('src'), 'img.property-img')

    # listing url
    link = card.find('a', class_='single-property-info')
    if link and link.get('href'):
        url = "https://www.century21.com" + link.get('href')
        add_field('listing_url', url, 'a.single-property-info')

    # price
    price = card.find('span', class_='price')
    if price:
        add_field('price', price.text, '.price')

    # MLS number
    mls = card.find('span', class_='mls-number')
    if mls:
        mls_text = mls.text.replace('MLS#', '').strip()
        add_field('MLS_number', mls_text, '.mls-number')

    # location
    address = card.find(class_='address')
    if address:
        add_field('location', address.text, '.address')

    # listed by
    listed_by = card.find('span', class_='listing-office')
    if listed_by:
        listed_text = listed_by.text.replace('Listed by:', '').strip()
        add_field('listed_by', listed_text, '.listing-office')

    # status
    status = card.find('span', class_='status-value')
    if status:
        add_field('status', status.text, '.status-value')

    # beds
    beds = card.find('span', class_='bed-info')
    if beds:
        add_field('beds', beds.text, '.bed-info')

    # baths
    baths = card.find('span', class_='bath-info')
    if baths:
        add_field('baths', baths.text, '.bath-info')

    # sq. ft
    sq_ft = card.find('span', class_='sq-ft-info')
    if sq_ft:
        add_field('sq_ft', sq_ft.text, '.sq-ft-info')

    record['fields'] = fields
    record['provenance'] = provenance
    new_records.append(record)

data['records'] = new_records
data['annotation_metadata']['total_records_extracted'] = len(new_records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Successfully created {len(new_records)} records and updated metadata.")
