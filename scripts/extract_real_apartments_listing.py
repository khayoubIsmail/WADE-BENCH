import json
import sys
import re
from lxml import html

sys.stdout.reconfigure(encoding='utf-8')

def get_xpath(node):
    return node.getroottree().getpath(node)

def get_css(node):
    path = []
    for anc in node.xpath('ancestor-or-self::*'):
        if anc.tag == 'html':
            continue
        step = anc.tag
        if anc.get('id'):
            step += '#' + anc.get('id')
            path = [step]
            continue
        siblings = anc.xpath(f'preceding-sibling::{anc.tag}')
        if siblings or anc.xpath(f'following-sibling::{anc.tag}'):
            step += f':nth-of-type({len(siblings) + 1})'
        path.append(step)
    return ' > '.join(path)

with open('data/raw_snapshots/realestate/SNAP_REAL_APARTMENTS_001_LISTING/page.html', 'rb') as f:
    parser = html.HTMLParser(encoding='utf-8')
    tree = html.fromstring(f.read(), parser=parser)

output_file = 'data/gold/by_task/realestate/WBV1_REAL_APARTMENTS_001_LISTING.json'

with open(output_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

listings = tree.xpath('//div[contains(@class, "property-snapshot-psr-panel")]')
records = []

def set_field(record, key, val, node, normalized_val=None, text_quote=None):
    if val is None or val == [] or val == {} or val == "":
        return
    if normalized_val is None:
        normalized_val = val
        
    record["fields"][key] = {"value": val, "normalized": normalized_val}
    
    if text_quote is None:
        if isinstance(val, str):
            text_quote = val[:50]
        elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
            text_quote = val[0][:50]
            
    css = get_css(node) if node is not None else ""
    xpath = get_xpath(node) if node is not None else ""
        
    if css or xpath:
        record["provenance"][key] = {
            "snapshot_id": "SNAP_REAL_APARTMENTS_001_LISTING",
            "css_selector": css,
            "xpath": xpath,
            "text_quote": text_quote
        }

for idx, listing in enumerate(listings):
    record = {
        "gold_record_id": f"WBV1_REAL_APARTMENTS_001_LISTING_{idx+1:03d}",
        "fields": {},
        "provenance": {}
    }
    
    set_field(record, "title", None, None)
    
    # Location (Full Address combined from street and city/zip)
    addr_node = listing.xpath('.//h2[contains(@class, "address-price-heading")]')
    if addr_node:
        street_node = listing.xpath('.//span[contains(@class, "street-address")]')
        city_node = listing.xpath('.//span[contains(@class, "city-st-zip")]')
        if street_node and city_node:
            street = street_node[0].text_content().strip().replace('\xa0', ' ')
            city = city_node[0].text_content().strip().replace('\xa0', ' ')
            # ensure comma separation
            if street and not street.endswith(','):
                full_addr = f"{street}, {city}"
            else:
                full_addr = f"{street} {city}"
            set_field(record, "location", full_addr, addr_node[0])
        else:
            # Fallback if specific spans aren't found
            full_addr = ' '.join(addr_node[0].text_content().replace('\xa0', ' ').split())
            set_field(record, "location", full_addr, addr_node[0])
        
    # Price
    price_node = listing.xpath('.//div[contains(@class, "price-normal")]')
    if price_node:
        set_field(record, "price", price_node[0].text_content().strip(), price_node[0])
        
    # Type house (ex. Condo, multi-family, single family)
    # the first li in description-summary
    desc_list = listing.xpath('.//div[contains(@class, "description-summary")]//li')
    if desc_list:
        set_field(record, "type_house", desc_list[0].text_content().strip(), desc_list[0])
        
    # Description summary
    if desc_list:
        desc_sum = [li.text_content().strip() for li in desc_list if li.text_content().strip()]
        if desc_sum:
            for d in desc_sum:
                if d.startswith("MLS #"):
                    set_field(record, "MLS_Number", d.replace("MLS #", "").strip(), desc_list[0])
            
    # Sq. Ft.
    sqft_node = listing.xpath('.//li[contains(@class, "sq.-ft.")]/div[contains(@class, "val")]')
    if sqft_node:
        set_field(record, "Sq_Ft", sqft_node[0].text_content().strip(), sqft_node[0])
        
    # Car Garage
    garage_node = listing.xpath('.//li[contains(@class, "car-garage")]/div[contains(@class, "val")]')
    if garage_node:
        set_field(record, "Car_Garage", garage_node[0].text_content().strip(), garage_node[0])
        
    # Full Baths
    fbath_node = listing.xpath('.//li[contains(@class, "full-baths")]/div[contains(@class, "val")]')
    if fbath_node:
        set_field(record, "Full_Baths", fbath_node[0].text_content().strip(), fbath_node[0])
        
    # Beds
    beds_node = listing.xpath('.//li[contains(@class, "beds")]/div[contains(@class, "val")]')
    if beds_node:
        set_field(record, "Beds", beds_node[0].text_content().strip(), beds_node[0])
        
    # Partial Bath
    pbath_node = listing.xpath('.//li[contains(@class, "partial-baths")]/div[contains(@class, "val")]')
    if pbath_node:
        set_field(record, "Partial_Bath", pbath_node[0].text_content().strip(), pbath_node[0])
        
    # by
    by_node = listing.xpath('.//div[contains(@class, "mls-info-attribution")]')
    if by_node:
        by_text = by_node[0].text_content().strip()
        by_text = re.sub(r'\s+', ' ', by_text).replace('Listed by ', '')
        set_field(record, "by", by_text, by_node[0])
        
    # images_urls
    imgs = listing.xpath('.//img[contains(@class, "psr-lazy") or contains(@class, "owl-lazy")]')
    img_urls = []
    for img in imgs:
        src = img.get('data-src-psr') or img.get('data-src') or img.get('src')
        if src and "spacer" not in src and "not-available" not in src:
            img_urls.append(src)
    if img_urls and imgs:
        set_field(record, "images_urls", img_urls, imgs[0])
        
    records.append(record)

data["records"] = records
data["annotation_metadata"]["total_records_extracted"] = len(records)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Extraction complete. Extracted {len(records)} records. Wrote to {output_file}")
