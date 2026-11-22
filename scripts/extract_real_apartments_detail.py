import json
import sys
import re
from lxml import html

sys.stdout.reconfigure(encoding='utf-8')

def get_xpath(node):
    if node is None:
        return ""
    try:
        return node.getroottree().getpath(node)
    except:
        return ""

def get_css(node):
    if node is None:
        return ""
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

with open('data/raw_snapshots/realestate/SNAP_REAL_APARTMENTS_002_DETAIL/page.html', 'rb') as f:
    parser = html.HTMLParser(encoding='utf-8')
    tree = html.fromstring(f.read(), parser=parser)

output_file = 'data/gold/by_task/realestate/WBV1_REAL_APARTMENTS_002_DETAIL.json'
with open(output_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# we will replace records
records = []

def set_field(record, key, val, node, normalized_val=None, text_quote=None, attribute=None, extra_attrs=None):
    if val is None or val == [] or val == {} or val == "":
        return
    if normalized_val is None:
        normalized_val = val
        
    field_data = {"value": val, "normalized": normalized_val}
    if extra_attrs:
        for k, v in extra_attrs.items():
            field_data[k] = v
            
    record["fields"][key] = field_data
    
    if text_quote is None:
        if isinstance(val, str):
            text_quote = val[:50]
        elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
            text_quote = val[0][:50]
        elif isinstance(val, int) or isinstance(val, float):
            text_quote = str(val)
        elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
            text_quote = str(val[0])[:50]
            
    css = get_css(node) if node is not None else ""
    xpath = get_xpath(node) if node is not None else ""
        
    if css or xpath:
        prov = {
            "snapshot_id": "SNAP_REAL_APARTMENTS_002_DETAIL",
            "css_selector": css,
            "xpath": xpath,
        }
        if attribute:
            prov["attribute"] = attribute
        if text_quote:
            prov["text_quote"] = text_quote
            
        record["provenance"][key] = prov

record = {
    "gold_record_id": "WBV1_REALESTATE_COLDWELLBANKER_001_DETAIL_001",
    "fields": {},
    "provenance": {}
}

# 1. listing_id
n = tree.xpath('//input[@id="listingId"]')
if n:
    set_field(record, "listing_id", n[0].get("value"), n[0], n[0].get("value"), attribute="value")

# 2. mls_number
n = tree.xpath('//*[@id="full-property-detail-body"]//li[contains(normalize-space(.), "MLS ID")]')
if n:
    mls_text = n[0].text_content().strip() # Get the li node
    mls_match = re.search(r'MLS ID[:\s]+(\d+)', mls_text)
    val = mls_match.group(1) if mls_match else mls_text
    set_field(record, "mls_number", val, n[0], val)

# 3. listing_url
n = tree.xpath('//link[@rel="canonical"]')
if n:
    set_field(record, "listing_url", n[0].get("href"), n[0], n[0].get("href"), attribute="href")

# 4. source_platform
set_field(record, "source_platform", "Coldwell Banker", None, "coldwell_banker")

# 5. location (user specified: "this is location not title listing_title")
n = tree.xpath('//h1[@id="main-content"]')
if n:
    val = n[0].text_content().strip()
    val = re.sub(r'\s+', ' ', val)
    set_field(record, "location", val, n[0], val)

# 6. address, street_address, city, state, postal_code, country, neighborhood, county, area, cross_streets
# Address parsing based on //h1[@id="main-content"] and script config
n = tree.xpath('//h1[@id="main-content"]')
if n:
    val = n[0].text_content().strip()
    val = re.sub(r'\s+', ' ', val)
    set_field(record, "address", val, n[0], "130 Maywood Drive, San Francisco, CA 94127, US")
    # hardcoded some normalization based on user template for now, could be dynamic
    set_field(record, "street_address", "130 Maywood Drive", None, "130 Maywood Drive")
    set_field(record, "city", "San Francisco", None, "San Francisco")
    set_field(record, "state", "CA", None, "California")
    set_field(record, "postal_code", "94127", None, "94127")
    set_field(record, "country", "US", None, "United States")

n_neigh = tree.xpath('//span[contains(text(), "Neighborhood")]/following-sibling::span')
if n_neigh:
    set_field(record, "neighborhood", n_neigh[0].text_content().strip(), n_neigh[0], n_neigh[0].text_content().strip())

n_county = tree.xpath('//span[contains(text(), "County")]/following-sibling::span')
if n_county:
    val = n_county[0].text_content().strip()
    set_field(record, "county", val, n_county[0], val + " County")

n_area = tree.xpath('//span[contains(text(), "Area")]/following-sibling::span')
if n_area:
    set_field(record, "area", n_area[0].text_content().strip(), n_area[0], n_area[0].text_content().strip())

n_cross = tree.xpath('//span[contains(text(), "Cross Streets")]/following-sibling::span')
if n_cross:
    val = n_cross[0].text_content().strip()
    set_field(record, "cross_streets", val, n_cross[0], val.replace('Dr', 'Drive'))

# 7. price
n = tree.xpath('//p[contains(@class,"price-block")]//span[@itemprop="price"]')
if n:
    val = n[0].text_content().strip()
    norm = int(re.sub(r'[^\d]', '', val))
    set_field(record, "price", val, n[0], norm)
    set_field(record, "price_currency", "USD", None, "USD")

# 8. status
n = tree.xpath('//span[contains(@class, "status")]')
if n:
    val = n[0].text_content().strip().replace('\u00c2\u00a0', ' ').replace('\xa0', ' ')
    set_field(record, "status", val, n[0], val.lower().replace(" ", "_").replace('sale_', ''))

# 8. Description
n = tree.xpath('//*[@id="property-description"]')
if n:
    desc = n[0].text_content().strip()
    set_field(record, "description", desc, n[0], desc)

# New Custom Fields
lis = tree.xpath('//*[@id="full-property-detail-body"]//li')
props = {}
for li in lis:
    strongs = li.xpath('strong')
    if strongs:
        key = strongs[0].text_content().strip().replace(':', '')
        val = li.text_content().replace(strongs[0].text_content(), '', 1).strip()
        val = re.sub(r'\s+', ' ', val)
        props[key] = (val, li)

def add_prop(field_name, key):
    if key in props:
        set_field(record, field_name, props[key][0], props[key][1], props[key][0])

add_prop("Price", "Price")
add_prop("HOA FEE", "HOA FEE")
add_prop("HOA FEE FREQ", "HOA FEE FREQ.")
add_prop("Status", "Status")
add_prop("Type", "Type")
add_prop("Source", "Source")
add_prop("MLS ID", "MLS ID")
add_prop("Updated", "Updated")
add_prop("Added to Site", "Added to Site")

listed_p = tree.xpath('//*[@id="full-property-detail-body"]//p[contains(text(), "Listed by")]')
if listed_p:
    listed_text = listed_p[0].text_content().strip()
    listed_match = re.search(r'Listed by\s+(.*)', listed_text)
    if listed_match:
        val = listed_match.group(1).strip()
        set_field(record, "Listed by", val, listed_p[0], val)

agent_name = tree.xpath('//div[contains(@class, "agent-list")]//p[contains(@class, "agent-name")]')
if agent_name:
    val = agent_name[0].text_content().strip()
    set_field(record, "Listing agent", val, agent_name[0], val)

logo_nodes = tree.xpath('//img[contains(@class, "logo") or contains(@class, "broker")]')
if logo_nodes:
    url = logo_nodes[0].get('src') or logo_nodes[0].get('data-src')
    if url:
        set_field(record, "logo url", url, logo_nodes[0], url)

# images_urls
img_nodes = tree.xpath('//*[contains(@class,"owl-lazy") or contains(@class,"psr-lazy")] | //*[@id="photo-gallery"]//img')
if not img_nodes:
    img_nodes = tree.xpath('//div[contains(@class,"owl-carousel")]//img')
if img_nodes:
    urls = []
    for node in img_nodes:
        url = node.get('data-src') or node.get('src')
        if url and "spacer" not in url.lower() and url not in urls:
            urls.append(url)
    if urls:
        set_field(record, "images_urls", urls, img_nodes[0], urls)

# 27. virtual_tour_url
n = tree.xpath('//a[contains(@class, "js-virtual-tour")]/@href')
if n:
    val = n[0]
    set_field(record, "virtual_tour_url", val, None, val)
    set_field(record, "3d_tour url", val, None, val)

# 9. summary facts
# We will parse out property_type, bedrooms, bathrooms_full, bathrooms_half, square_feet, garage_spaces
n_ul = tree.xpath('//ul[contains(@class,"details") and contains(@class,"action-bar-feature")]')
if n_ul:
    n_ul = n_ul[0]
    items = [li.text_content().strip() for li in n_ul.xpath('./li')]
    filtered = [i for i in items if 'Sale' not in i and 'Pending' not in i and 'Updated' not in i and 'days ago' not in i]
    if filtered:
        title_val = ''.join(filtered)
        set_field(record, "listing_title", title_val, n_ul, title_val)

    for item in items:
        if "Single Family" in item:
            set_field(record, "property_type", "Single Family", n_ul, "single_family")
            set_field(record, "sale_type", "For Sale", n_ul, "for_sale")
        elif "Beds" in item:
            set_field(record, "bedrooms", item, n_ul, int(re.search(r'\d+', item).group()))
        elif "Full Baths" in item:
            set_field(record, "bathrooms_full", item, n_ul, int(re.search(r'\d+', item).group()))
        elif "Partial Bath" in item:
            set_field(record, "bathrooms_half", item, n_ul, int(re.search(r'\d+', item).group()))
        elif "Sq. Ft." in item:
            set_field(record, "square_feet", item, n_ul, int(re.sub(r'[^\d]', '', item)))
        elif "Car Garage" in item:
            set_field(record, "garage_spaces", item, n_ul, int(re.search(r'\d+', item).group()))
            
    # sum baths
    try:
        total_baths = int(record["fields"].get("bathrooms_full", {}).get("normalized", 0)) + \
                      int(record["fields"].get("bathrooms_half", {}).get("normalized", 0))
        set_field(record, "bathrooms_total", f"{total_baths} total baths", None, total_baths)
    except:
        pass

# 10. photo_count
n = tree.xpath('//*[contains(@class,"owl-carousel") and @data-photocount]')
if n:
    val = n[0].get('data-photocount')
    set_field(record, "photo_count", f"{val} Photos", n[0], int(val), attribute="data-photocount")

# 11. primary_image_url
n = tree.xpath('//meta[@property="og:image"]')
if n:
    val = n[0].get('content')
    set_field(record, "primary_image_url", val, n[0], val, attribute="content")

# 12. virtual_tour_url / 3d_tour url
n = tree.xpath('//a[contains(@href,"matterport.com")]')
if n:
    val = n[0].get('href')
    set_field(record, "3d_tour url", val, n[0], val, attribute="href")

# 13. date_posted, updated_date, added_to_site
set_field(record, "date_posted", "2026-05-27T00:00:00-04:00", None, "2026-05-27")
n = tree.xpath('//span[contains(text(), "Updated")]/following-sibling::span')
if n:
    set_field(record, "updated_date", n[0].text_content().strip(), n[0], "2026-06-05")
set_field(record, "updated_relative", "Updated 6 days ago", None, "updated_6_days_ago")

n = tree.xpath('//span[contains(text(), "Added to Site")]/following-sibling::span')
if n:
    set_field(record, "added_to_site", n[0].text_content().strip(), n[0], "15_days_ago")

# 14. description
n = tree.xpath('//div[contains(@class,"remark-section")]')
if n:
    val = n[0].text_content().strip()
    val = re.sub(r'\s+', ' ', val)
    set_field(record, "description", val, n[0], "Traditional Pacific Ocean view single-family home with 4 bedrooms, 3 bathrooms, remodeled kitchen and baths, formal living and dining rooms, lower-level family/media room, home gym space, landscaped backyard, and ocean/panoramic views.")

# 15. Coordinates
n = tree.xpath('//script[@id="json-pd-init"]')
if n:
    script_text = n[0].text_content()
    try:
        pd_data = json.loads(script_text)
        lat = pd_data.get("lat")
        lng = pd_data.get("lng")
        set_field(record, "latitude", lat, n[0], lat)
        set_field(record, "longitude", lng, n[0], lng)
    except:
        pass

# 16. full property details loop
def get_detail_val(label_text):
    n = tree.xpath(f'//*[@id="full-property-detail-body"]//span[contains(text(), "{label_text}")]/following-sibling::span')
    if n:
        return n[0].text_content().strip(), n[0]
    return None, None

fields_mapping = [
    ("number_of_rooms", "Number of Rooms", lambda x: int(x)),
    ("rooms_areas", "Rooms/Areas", lambda x: [s.strip() for s in x.split(',')]),
    ("interior_features", "Interior Features", lambda x: [s.strip() for s in x.split(',')]),
    ("fireplace", "Fireplace", lambda x: x.lower() == 'yes'),
    ("number_of_fireplaces", "Number of Fireplaces", lambda x: int(x)),
    ("fireplace_features", "Fireplace Features", lambda x: [s.strip() for s in x.split(',')]),
    ("appliances", "Appliances", lambda x: [s.strip() for s in x.split(',')]),
    ("flooring", "Flooring", lambda x: [s.strip() for s in x.split(',')]),
    ("bathroom_features", "Bathroom Features", lambda x: [s.strip() for s in x.split(',')]),
    ("primary_bathroom", "Primary Bathroom", lambda x: [s.strip() for s in x.split(',')]),
    ("primary_bedroom", "Primary Bedroom", lambda x: [s.strip() for s in x.split(',')]),
    ("bedroom_1", "Bedroom 1", lambda x: [s.strip() for s in x.split(',')]),
    ("kitchen_features", "Kitchen Features", lambda x: [s.strip() for s in x.split(',')]),
    ("dining_room", "Dining Room", lambda x: x),
    ("laundry", "Laundry", lambda x: "Inside Room"), # Custom logic due to duplicate
    ("exterior_features", "Exterior Features", lambda x: [s.strip() for s in x.split(',')]),
    ("garage", "Garage", lambda x: x.lower() == 'yes'),
    ("parking_features", "Parking Features", lambda x: [s.strip().replace(' (Single Family Only)', '') for s in x.split(',')]),
    ("association", "Association", lambda x: x.lower() == 'yes'),
    ("association_name", "Association Name", lambda x: x),
    ("hoa_fee_frequency", "HOA Fee Freq", lambda x: x.lower()),
    ("association_fee_frequency", "Association Fee Frequency", lambda x: x.lower()),
    ("heating_type", "Heating Type", lambda x: [s.strip() for s in x.split(',')]),
    ("cooling", "Cooling", lambda x: x),
    ("sewer", "Sewer", lambda x: x),
    ("water", "Water", lambda x: x),
    ("utility_description", "Utility Description", lambda x: x),
    ("architectural_style", "Architectural Style", lambda x: [s.strip() for s in x.split(',')]),
    ("basement_description", "Basement Description", lambda x: x),
    ("foundation", "Foundation", lambda x: x),
    ("roof", "Roof", lambda x: [s.strip() for s in x.split(',')]),
    ("windows", "Windows", lambda x: x),
    ("square_feet_source", "Square Feet Source", lambda x: x),
    ("living_area", "Living Area", lambda x: int(re.sub(r'[^\d]', '', x))),
    ("current_building_use", "Current Building Use", lambda x: x),
    ("year_built", "Year Built", lambda x: int(x)),
    ("property_view", "Property View", lambda x: [s.strip() for s in x.split(',')]),
    ("lot_size_acres", "Lot Size Acres", lambda x: float(x)),
    ("lot_size_sqft", "Lot Size Sqft", lambda x: int(re.sub(r'[^\d]', '', x))),
    ("street_road_description", "Street/Road Description", lambda x: x),
    ("road_maintenance", "Road Maintenance", lambda x: x),
    ("lot_features", "Lot Features", lambda x: [s.strip().replace('(s)', 's').replace('Grass Artificial', 'Artificial Grass') for s in x.split(',')]),
    ("fencing", "Fencing", lambda x: [s.strip() for s in x.split(',')]),
    ("special_conditions", "Special Conditions", lambda x: x),
    ("apn", "APN", lambda x: x),
]

for key, label, norm_func in fields_mapping:
    val, node = get_detail_val(label)
    if val:
        try:
            norm = norm_func(val)
        except:
            norm = val
        set_field(record, key, val, node, norm)

# Custom fee logic
fee, node = get_detail_val("HOA Fee")
if fee:
    set_field(record, "hoa_fee", "$2/month", node, {"amount": 2, "currency": "USD", "period": "month"})

assoc_fee, node = get_detail_val("Association Fee")
if assoc_fee:
    set_field(record, "association_fee", "$27", node, {"amount": 27, "currency": "USD"})

# Agent / Office
n = tree.xpath('//*[@id="full-property-detail-body"]//p[contains(@class,"mls-idx")]//span[contains(@class,"attr-idx")]')
if n:
    set_field(record, "listing_agent", n[0].text_content().strip(), n[0], n[0].text_content().strip())

n = tree.xpath('//*[@id="full-property-detail-body"]//p[contains(@class,"mls-idx")]//span[contains(@class,"office-name")]')
if n:
    set_field(record, "listing_office", n[0].text_content().strip(), n[0], n[0].text_content().strip())

set_field(record, "listing_agent_license", None, None, None, extra_attrs={"_note": "CalRE# not present in the page for current listing agent Andrew Herrera II; CalRE# 01860593 on page belongs to selling agent Steed Ahn from the 2021 transaction"})

set_field(record, "open_house_scheduled", False, None, False)

# Schools
n = tree.xpath('//*[@id="school-body"]//h4')
if n:
    set_field(record, "school_district", "San Francisco Unified School District", n[0], "San Francisco Unified School District")

schools_rows = tree.xpath('//*[@id="school-body"]//table//tr')
if len(schools_rows) > 1:
    schools_val = []
    schools_norm = []
    for row in schools_rows[1:]: # skip header
        cols = row.xpath('./th | ./td')
        if len(cols) >= 3:
            name_div = cols[0].xpath('.//div[contains(@class,"school-name")]')
            addr_div = cols[0].xpath('.//div[contains(@class,"school-address")]')
            name = name_div[0].text_content().strip() if name_div else cols[0].text_content().strip()
            addr = addr_div[0].text_content().strip() if addr_div else ""
            grades = cols[1].text_content().strip() if len(cols)>1 else ""
            dist = cols[2].text_content().strip() if len(cols)>2 else ""
            try:
                dist_f = float(dist.split()[0])
            except:
                dist_f = 0.0
                
            level = "elementary"
            if "Middle" in name: level = "middle"
            elif "High" in name: level = "high"
            
            schools_val.append({
                "name": name,
                "address": addr,
                "grades": grades,
                "distance_miles": dist_f
            })
            schools_norm.append({
                "name": name,
                "address": addr,
                "grades": grades,
                "level": level,
                "distance_miles": dist_f
            })
            
    if schools_val:
        set_field(record, "nearby_schools", schools_val, schools_rows[1], schools_norm, text_quote=schools_val[0]["name"])

# tax_history
tax_rows = tree.xpath('//div[contains(@class,"tax-history-table")]//div[contains(@class,"tax-history-row")]')
if tax_rows:
    tax_val = []
    tax_norm = []
    for row in tax_rows:
        cols = row.xpath('.//div[contains(@class,"tax-history-data")]')
        if len(cols) >= 5:
            y = int(cols[0].text_content().strip())
            pt = cols[1].text_content().strip()
            tc = cols[2].text_content().strip()
            ta = cols[3].text_content().strip()
            ac = cols[4].text_content().strip()
            
            tax_val.append({
                "year": y, "property_taxes": pt, "tax_change_pct": tc if tc not in ["-", "—", "\u2014"] else None,
                "tax_assessment": ta, "assessment_change_pct": ac if ac not in ["-", "—", "\u2014"] else None
            })
            
            def parse_amt(x):
                try: return int(re.sub(r'[^\d]', '', x))
                except: return None
            def parse_pct(x):
                try: return float(x.replace('%', ''))
                except: return None
                
            tax_norm.append({
                "year": y, "property_taxes_usd": parse_amt(pt), "tax_change_pct": parse_pct(tc),
                "tax_assessment_usd": parse_amt(ta), "assessment_change_pct": parse_pct(ac)
            })
            
    if tax_val:
        set_field(record, "tax_history", tax_val, tax_rows[0], tax_norm, text_quote=f"{tax_val[0]['year']} {tax_val[0]['property_taxes']}")

# price_sale_history
hist_rows = tree.xpath('//div[contains(@class,"price-history-table")]//div[contains(@class,"price-history-row")]')
if hist_rows:
    hist_val = []
    hist_norm = []
    for row in hist_rows:
        cols = row.xpath('.//div[contains(@class,"price-history-data")]')
        if len(cols) >= 5:
            dt = cols[0].text_content().strip()
            ev = cols[1].text_content().strip()
            pr = cols[2].text_content().strip()
            cp = cols[3].text_content().strip()
            sr = cols[4].text_content().strip()
            
            hist_val.append({
                "date": dt, "event": ev, "price": pr, "change_pct": cp if cp not in ["-", "—", "\u2014"] else None, "source": sr
            })
            
            def parse_amt(x):
                try: return int(re.sub(r'[^\d]', '', x))
                except: return None
            def parse_pct(x):
                try: return float(x.replace('%', ''))
                except: return None
            def parse_date(x):
                parts = x.split('/')
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                return x
                
            hist_norm.append({
                "date": parse_date(dt), "event": ev.lower().replace(' ', '_'), "price_usd": parse_amt(pr),
                "change_pct": parse_pct(cp), "source": sr.lower().replace(' ', '_')
            })
            
    if hist_val:
        set_field(record, "price_sale_history", hist_val, hist_rows[0], hist_norm, text_quote=f"{hist_val[0]['date']} {hist_val[0]['event']} {hist_val[0]['price']}")

# data_source
set_field(record, "data_source", "San_Francisco", None, "San Francisco MLS")


records.append(record)

data["records"] = records
if "annotation_metadata" not in data:
    data["annotation_metadata"] = {}
data["annotation_metadata"]["total_records_extracted"] = len(records)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Extraction complete. Wrote {len(records)} records.")
