"""
fix_realestate_gold.py
Applies all standardization fixes to all 20 real estate gold JSON files.
Decisions:
  - location -> address (all files)
  - price.normalized -> structured dict
  - bed/bath normalized -> int
  - relative dates -> null
  - field name canonicalization (all)
  - Non-English fields in LEBONCOIN/FINN_EIENDOM: KEEP as-is
  - first review in RIGHTMOVE_002: KEEP as-is
"""

import json
import os
import re
import shutil

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
BACKUP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate_backup'

# ── Backup ──────────────────────────────────────────────────────────────────
os.makedirs(BACKUP_DIR, exist_ok=True)
for fname in os.listdir(GOLD_DIR):
    if fname.endswith('.json'):
        shutil.copy2(os.path.join(GOLD_DIR, fname), os.path.join(BACKUP_DIR, fname))
print("Backup created at:", BACKUP_DIR)

# ── Field rename map ─────────────────────────────────────────────────────────
FIELD_RENAMES = {
    'beedrooms': 'bedrooms',
    'beds': 'bedrooms',
    'Bedroom': 'bedrooms',
    'Total_Bedrooms': 'bedrooms',
    'Total_Bathrooms': 'bathrooms',
    'Total_bathrooms': 'bathrooms',
    'listed_by': 'listing_agent',
    'agent_listing': 'listing_agent',
    'by': 'listing_agent',
    'agent': 'listing_agent',
    'Open_House_time': 'open_house_schedule',
    'open_time': 'open_house_schedule',
    'image_url': 'images_urls',
    'image': 'images_urls',
    'title': 'listing_title',
    'agent_branding': 'listing_office',
    'agent_branding_name': 'listing_office',
    'agent_branding_logo': 'listing_agent_logo',
    'agent_branding_phone': 'listing_agent_phone',
    'agent_branding_location': 'listing_agent_location',
    'agent_branding_negotiator_name': 'listing_agent_name',
    'agent_branding_negotiator_phone': 'listing_agent_phone',
    'agent_branding_negotiator_pic': 'listing_agent_photo',
    'agent_logo': 'listing_agent_logo',
    'agent_phone': 'listing_agent_phone',
    'agent_website': 'listing_agent_website',
    'logo_agent': 'listing_agent_logo',
    'phone': 'listing_agent_phone',
    'type': 'property_type',
    'type_house': 'property_type',
    'published date': 'published_date',
    'published_day': 'published_date',
    'published_or_posted': 'published_date',
    'sq_ft': 'floor_area',
    'Sq_Ft': 'floor_area',
    'sq. ft.': 'floor_area',
    'sq._ft.': 'floor_area',
    'Sq._Ft': 'floor_area',
    'Square_Feet': 'floor_area',
    'area': 'floor_area',
    'lot_size': 'land_area',
    'Partial_Bath': 'bathrooms_partial',
    'location': 'address',
    # RIGHTMOVE_002 uppercase / mixed-case
    'BEDROOMS': 'bedrooms',
    'BATHROOMS': 'bathrooms',
    'PROPERTY TYPE': 'property_type',
    'Furnish type': 'furnish_type',
    'Key features': 'key_features',
    'Description': 'description',
    'PARKING': 'parking',
}

# ── Currency detection ────────────────────────────────────────────────────────
CURRENCY_MAP = [
    (r'£',     {'name': 'British pound',     'code': 'GBP', 'symbol': '£'}),
    (r'NZ\$',  {'name': 'New Zealand dollar', 'code': 'NZD', 'symbol': 'NZ$'}),
    (r'US\$',  {'name': 'US dollar',          'code': 'USD', 'symbol': '$'}),
    (r'\$',    {'name': 'US dollar',          'code': 'USD', 'symbol': '$'}),
    (r'€',     {'name': 'Euro',               'code': 'EUR', 'symbol': '€'}),
    (r'\bkr\b',{'name': 'Norwegian krone',    'code': 'NOK', 'symbol': 'kr'}),
    (r'\bMAD\b',{'name': 'Moroccan dirham',   'code': 'MAD', 'symbol': 'MAD'}),
    (r'\bDH\b', {'name': 'Moroccan dirham',   'code': 'MAD', 'symbol': 'MAD'}),
]

# Files where $ = NZD
NZD_FILES = {'WBV1_REAL_REALESTATE.CO.NZ_001_LISTING.json', 'WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL.json'}


def detect_currency(value_str, fname):
    if fname in NZD_FILES and '$' in value_str:
        return {'name': 'New Zealand dollar', 'code': 'NZD', 'symbol': 'NZ$'}
    for pattern, info in CURRENCY_MAP:
        if re.search(pattern, value_str):
            return info
    return None


def parse_amount(value_str):
    """Extract numeric amount from a price string."""
    # Remove currency symbols and text, keep digits, commas, periods, spaces
    cleaned = re.sub(r'[£$€NZkrMADDH\s]', '', value_str, flags=re.IGNORECASE)
    # Remove any remaining non-numeric except . and ,
    cleaned = re.sub(r'[^\d.,]', '', cleaned)
    # Remove thousands separators (commas in EN, spaces in FR/NO, periods in some)
    # Detect if comma is decimal separator (e.g. Norwegian: "3.290.000")
    cleaned = cleaned.replace('.', '').replace(',', '').replace(' ', '')
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_price(value_str, fname):
    if not isinstance(value_str, str):
        return value_str
    currency = detect_currency(value_str, fname)
    amount = parse_amount(value_str)
    if currency and amount is not None:
        return {'amount': amount, 'currency': currency}
    return value_str  # keep as-is if can't parse


def normalize_integer(value):
    """Convert a string integer to int if possible."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(str(value).strip())
        except ValueError:
            return value
    return value


RELATIVE_DATE_PATTERNS = [
    r'^yesterday$', r'^today$', r'^\d+ day', r'^\d+ hour',
    r'ago$', r'^just now$', r'^recently$',
]


def is_relative_date(val):
    if not isinstance(val, str):
        return False
    for p in RELATIVE_DATE_PATTERNS:
        if re.search(p, val, re.IGNORECASE):
            return True
    return False


def rename_fields(obj, file_name):
    """Recursively rename fields in a dict (fields and provenance)."""
    if not isinstance(obj, dict):
        return obj
    new_obj = {}
    for k, v in obj.items():
        new_key = FIELD_RENAMES.get(k, k)
        new_obj[new_key] = rename_fields(v, file_name)
    return new_obj


# ── Files to process ─────────────────────────────────────────────────────────
files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

stats = {}

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get('records', [])
    counts = {'field_renames': 0, 'price_fixes': 0, 'int_fixes': 0, 'date_fixes': 0}

    new_records = []
    for rec in records:
        # 1. Rename fields in fields dict
        old_fields = rec.get('fields', {})
        new_fields_keys = list(old_fields.keys())
        renamed_fields = {}
        for k, v in old_fields.items():
            new_k = FIELD_RENAMES.get(k, k)
            if new_k != k:
                counts['field_renames'] += 1
            renamed_fields[new_k] = v

        # 2. Rename fields in provenance dict
        old_prov = rec.get('provenance', {})
        renamed_prov = {}
        for k, v in old_prov.items():
            new_k = FIELD_RENAMES.get(k, k)
            renamed_prov[new_k] = v

        # 3. Fix price normalization
        if 'price' in renamed_fields:
            pf = renamed_fields['price']
            norm = pf.get('normalized')
            if isinstance(norm, str):
                new_norm = normalize_price(norm, fname)
                if new_norm != norm:
                    pf['normalized'] = new_norm
                    counts['price_fixes'] += 1
            elif isinstance(norm, dict) and 'amount' not in norm:
                val_str = pf.get('value', '')
                if isinstance(val_str, str):
                    new_norm = normalize_price(val_str, fname)
                    if isinstance(new_norm, dict):
                        pf['normalized'] = new_norm
                        counts['price_fixes'] += 1

        # 4. Fix bedroom/bathroom normalized to int
        for bed_field in ['bedrooms', 'bathrooms']:
            if bed_field in renamed_fields:
                bf = renamed_fields[bed_field]
                norm = bf.get('normalized')
                new_norm = normalize_integer(norm)
                if new_norm != norm:
                    bf['normalized'] = new_norm
                    counts['int_fixes'] += 1

        # 5. Fix relative dates → null
        if 'published_date' in renamed_fields:
            df = renamed_fields['published_date']
            norm = df.get('normalized')
            if is_relative_date(norm):
                df['normalized'] = None
                counts['date_fixes'] += 1

        rec['fields'] = renamed_fields
        rec['provenance'] = renamed_prov
        new_records.append(rec)

    data['records'] = new_records
    data['annotation_metadata']['total_records_extracted'] = len(new_records)

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    stats[fname] = counts
    total = sum(counts.values())
    print("%-60s  renames=%d  price=%d  int=%d  date=%d  TOTAL=%d" % (
        fname, counts['field_renames'], counts['price_fixes'],
        counts['int_fixes'], counts['date_fixes'], total))

print()
print("Done.")
