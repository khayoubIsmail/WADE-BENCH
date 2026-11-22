"""
fix_realestate_gold_pass3.py
Fixes:
  1. Numeric normalization for area/count fields (float + unit, or int)
  2. Provenance: add attribute, css_selector_absolute, xpath_absolute fields
"""

import json, os, re

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

# Fields that should be FLOAT with a unit
AREA_FIELDS = {'floor_area', 'land_area', 'lot_size', 'price_per_m2', 'monthly_fees', 'total_price'}
# Fields that should be INT
INT_FIELDS = {'rooms', 'year_built', 'review_count', 'Car_Garage', 'parking_or_garage_spaces',
              'bathrooms_partial', 'floor_level', 'bedrooms', 'bathrooms'}


def detect_unit(value_str):
    """Return unit string from a value string."""
    s = value_str.lower()
    if 'm²' in s or 'm2' in s or ' m²' in s:
        return 'm2'
    if 'sq. ft.' in s or 'sqft' in s or 'sq ft' in s or 'sq.ft' in s:
        return 'sqft'
    if 'acre' in s:
        return 'acre'
    return None


def parse_number(value_str):
    """Extract numeric value from a string."""
    if not isinstance(value_str, str):
        return None
    cleaned = re.sub(r'[^\d.,]', '', value_str)
    # remove thousands separators (trailing ,000 pattern or space-separated digits)
    # treat comma as thousands separator if followed by 3 digits
    cleaned = re.sub(r',(\d{3})', r'\1', cleaned)
    cleaned = cleaned.replace(',', '.')
    # take first valid number
    m = re.search(r'[\d]+\.?\d*', cleaned)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


def normalize_numeric_fields(fields):
    """Fix normalized values for numeric fields."""
    changes = 0
    for field_name, field_val in fields.items():
        if not isinstance(field_val, dict):
            continue
        value = field_val.get('value')
        norm = field_val.get('normalized')

        if field_name in AREA_FIELDS and isinstance(norm, str):
            num = parse_number(norm if norm else value)
            unit = detect_unit(value if isinstance(value, str) else '')
            if num is not None:
                field_val['normalized'] = num
                if unit and 'unit' not in field_val:
                    field_val['unit'] = unit
                changes += 1

        elif field_name in INT_FIELDS and isinstance(norm, str):
            num = parse_number(norm)
            if num is not None:
                field_val['normalized'] = int(num)
                changes += 1

    return changes


# Fields where attribute = "href" (URL fields)
HREF_FIELDS = {'listing_url', 'agent_website', 'listing_agent_website'}
# Fields where attribute = "src" (image fields)
SRC_FIELDS = {'images_urls', 'image_url', 'listing_agent_logo', 'listing_agent_photo',
              'logo_agent', 'agent_branding_logo', 'primary_image_url'}
# Fields where attribute = "content" (meta fields)
CONTENT_FIELDS = {'primary_image_url_meta'}


def get_attribute(field_name):
    if field_name in HREF_FIELDS:
        return 'href'
    if field_name in SRC_FIELDS:
        return 'src'
    if field_name in CONTENT_FIELDS:
        return 'content'
    return None


def fix_provenance(prov):
    """Add missing provenance fields: attribute, css_selector_absolute, xpath_absolute."""
    changes = 0
    for field_name, prov_val in prov.items():
        if not isinstance(prov_val, dict):
            continue

        # Add attribute if missing
        if 'attribute' not in prov_val:
            prov_val['attribute'] = get_attribute(field_name)
            changes += 1

        # Handle xpath: if current xpath is absolute (starts with /html), rename to xpath_absolute
        # and try to derive stable xpath from css_selector
        current_xpath = prov_val.get('xpath', '')
        if 'xpath_absolute' not in prov_val:
            if current_xpath and current_xpath.startswith('/html'):
                # Move it to xpath_absolute
                prov_val['xpath_absolute'] = current_xpath
                # Derive a stable xpath from css_selector if available
                css = prov_val.get('css_selector', '')
                if css and not css.startswith('div >') and 'nth-of-type' not in css:
                    # Convert simple CSS to xpath approximation
                    stable_xpath = css_to_xpath_approx(css, field_name)
                    prov_val['xpath'] = stable_xpath
                else:
                    prov_val['xpath'] = None  # no stable version derivable
                changes += 1
            else:
                # xpath is already stable or absent
                prov_val['xpath_absolute'] = None
                changes += 1

        # Handle css_selector: if it looks like an absolute chain (nth-of-type heavy), move it
        if 'css_selector_absolute' not in prov_val:
            current_css = prov_val.get('css_selector', '')
            if current_css and current_css.count('nth-of-type') >= 2:
                # It's an absolute chain — move to css_selector_absolute
                prov_val['css_selector_absolute'] = current_css
                prov_val['css_selector'] = None  # no stable version available
            else:
                # Already stable or short — keep as-is, set absolute to None
                prov_val['css_selector_absolute'] = None
            changes += 1

    return changes


def css_to_xpath_approx(css, field_name):
    """Convert simple CSS selector to an approximate stable XPath."""
    # Handle common simple patterns
    css = css.strip()
    
    # [data-testid='xxx'] → //*[@data-testid='xxx']
    m = re.match(r"^\[([^=]+)='([^']+)'\]$", css)
    if m:
        return "//*[@%s='%s']" % (m.group(1), m.group(2))
    
    # tag.class → //tag[contains(@class,'class')]
    m = re.match(r'^(\w+)\.(\S+)$', css)
    if m:
        return "//%s[contains(@class,'%s')]" % (m.group(1), m.group(2))
    
    # tag#id → //tag[@id='id']
    m = re.match(r'^(\w+)#(\S+)$', css)
    if m:
        return "//%s[@id='%s']" % (m.group(1), m.group(2))
    
    # link[rel='canonical'] → //link[@rel='canonical']
    m = re.match(r'^(\w+)\[([^\]]+)\]$', css)
    if m:
        tag = m.group(1)
        attr_part = m.group(2)
        # attr_part like rel='canonical'
        am = re.match(r"(\w+)='([^']+)'", attr_part)
        if am:
            return "//%s[@%s='%s']" % (tag, am.group(1), am.group(2))
    
    # Simple tag or class
    if re.match(r'^\w+$', css):
        return '//' + css
    
    return None  # can't derive


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    num_changes = 0
    prov_changes = 0

    for rec in data.get('records', []):
        num_changes += normalize_numeric_fields(rec.get('fields', {}))
        prov_changes += fix_provenance(rec.get('provenance', {}))

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = num_changes + prov_changes
    if total > 0:
        print("%-60s  numeric=%d  provenance=%d" % (fname, num_changes, prov_changes))

print("\nDone.")
