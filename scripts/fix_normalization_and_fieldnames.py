"""
fix_normalization_and_fieldnames.py
Fixes:
  1. Date normalization: non-ISO dates → ISO 8601 (YYYY-MM-DD)
  2. Field-name standardization per WADE-Bench guidelines
  3. Remaining xpath absolute issues (2 remaining)
"""

import json, os, re
from datetime import datetime

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

# ─── Canonical field name mapping ─────────────────────────────────────────────
CANON = {
    # bedrooms
    'Beds': 'bedrooms', 'Bed': 'bedrooms', 'bed': 'bedrooms', 'beds': 'bedrooms',
    'bedroom': 'bedrooms', 'bedroom_count': 'bedrooms', 'bedrooms_count': 'bedrooms',
    'number_of_bedrooms': 'bedrooms', 'Nombre de chambres': 'bedrooms',
    # bathrooms
    'Baths': 'bathrooms', 'Bath': 'bathrooms', 'bath': 'bathrooms', 'baths': 'bathrooms',
    'bathroom': 'bathrooms', 'bathroom_count': 'bathrooms', 'bathrooms_count': 'bathrooms',
    'number_of_bathrooms': 'bathrooms', 'Full_Baths': 'bathrooms', 'Total_Baths': 'bathrooms',
    'Full_bathrooms': 'bathrooms', 'Nombre de salles d\'eau': 'bathrooms',
    # floor_area
    'sqft': 'floor_area', 'floor_size': 'floor_area', 'internal_area': 'floor_area',
    'living_area': 'floor_area', 'Living_area': 'floor_area', 'Living_Area': 'floor_area',
    'Sq._Ft.': 'floor_area', 'Surface habitable': 'floor_area',
    'Use_Area': 'floor_area',
    # land_area
    'lot_area': 'land_area', 'land': 'land_area', 'land_size': 'land_area',
    'plot_size': 'land_area', 'Lot_area': 'land_area',
    # price
    'Price': 'price', 'asking_price': 'price', 'listing_price': 'price',
    'Prix du bien': 'price',
    # address
    'property_address': 'address', 'Location': 'address',
    # listing_agent
    'listed_by': 'listing_agent', 'Listed_by': 'listing_agent', 'agent': 'listing_agent',
    'broker_name': 'listing_agent', 'Listing_Agent': 'listing_agent',
    # listing_office
    'Listing_Office': 'listing_office', 'office': 'listing_office',
    'brokerage': 'listing_office', 'agency': 'listing_office',
    # mls_number
    'MLS_Number': 'mls_number', 'MLS_number': 'mls_number', 'MLS_ID': 'mls_number',
    'MLS#': 'mls_number', 'mlsNumber': 'mls_number', 'mls': 'mls_number',
    # listing_id
    'Reference': 'listing_id', 'annonce_id': 'listing_id', 'property_id': 'listing_id',
    'Listing_ID_#': 'listing_id',
    # energy_rating
    'energy_class': 'energy_rating', 'BER': 'energy_rating', 'ber': 'energy_rating',
    'energy class': 'energy_rating', 'Classe énergie': 'energy_rating',
    # year_built
    'Year_Built': 'year_built', 'Year_built': 'year_built',
    'Year_of_construction': 'year_built',
    # date fields
    'Date_listed': 'listed_date', 'date_listed': 'listed_date',
    'listed_datetime': 'listed_date',
    # rooms (keep as rooms for now — LBC uses it for nb_pieces)
    'Nombre de pièces': 'rooms', 'Nombre de pi\u00e8ces': 'rooms',
    # Mensualités → monthly_fees
    'Mensualit\u00e9s': 'monthly_fees',
    # Type de bien → property_type
    'Type de bien': 'property_type',
    # Vendu par → listing_agent (sold by)
    'Vendu par': 'listing_agent',
    # Building_area: map to floor_area ONLY if floor_area doesn't already exist
    'Building_area': 'floor_area',
}

# Fields to SKIP (don't rename, keep site-specific)
KEEP_AS_IS = {
    'bathrooms_partial', 'Car_Garage', 'price_per_m2', 'price_per_sqft',
    'APN', 'apn', 'BER_No', 'finnkode',
}


# ─── Date parsing ──────────────────────────────────────────────────────────────
DATE_FMTS = [
    '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d',
    '%d/%m/%y', '%m/%d/%y',
    '%B %d, %Y', '%b %d, %Y',
    '%d %B %Y', '%d %b %Y',
]


def parse_to_iso(val):
    if not isinstance(val, str): return None
    val = val.strip()
    # Already ISO
    if re.match(r'^\d{4}-\d{2}-\d{2}(T.*)?$', val):
        return None  # already correct
    # Try formats
    for fmt in DATE_FMTS:
        try:
            dt = datetime.strptime(val, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None


# ─── Main processing ──────────────────────────────────────────────────────────
files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    field_changes = 0
    date_changes = 0
    xpath_changes = 0

    for rec in data.get('records', []):
        fields = rec.get('fields', {})
        prov   = rec.get('provenance', {})

        # ── 1. Date normalization ─────────────────────────────────────────────
        for fn, fv in list(fields.items()):
            if not isinstance(fv, dict): continue
            norm = fv.get('normalized')
            val  = fv.get('value')
            if isinstance(norm, str) and not re.match(r'^\d{4}-\d{2}-\d{2}', norm):
                iso = parse_to_iso(norm) or parse_to_iso(str(val) if val else '')
                if iso:
                    fv['normalized'] = iso
                    date_changes += 1

        # ── 2. Field-name standardization ─────────────────────────────────────
        renames = {}  # old_name -> new_name
        for fn in list(fields.keys()):
            if fn in KEEP_AS_IS:
                continue
            canon = CANON.get(fn)
            if canon and canon != fn:
                # Only rename if canonical name doesn't already exist with data
                if canon not in fields or fields[canon] is None:
                    renames[fn] = canon
                elif fn == 'Building_area' and 'floor_area' in fields:
                    # Keep as building_area since floor_area already has a value
                    renames[fn] = 'building_area'
                else:
                    # Canonical already exists — check if values differ
                    existing_val = fields[canon].get('value') if isinstance(fields[canon], dict) else None
                    new_val = fields[fn].get('value') if isinstance(fields[fn], dict) else None
                    if existing_val and new_val and existing_val != new_val:
                        # Keep both but rename incoming to avoid conflict
                        pass  # keep fn as-is
                    else:
                        # Same value or one is None — drop the non-canonical
                        renames[fn] = None  # means delete

        for old_fn, new_fn in renames.items():
            val = fields.pop(old_fn, None)
            pv  = prov.pop(old_fn, None)
            if new_fn is not None:
                if new_fn not in fields:
                    fields[new_fn] = val
                if pv is not None and new_fn not in prov:
                    # Update snapshot_id / field references in provenance
                    prov[new_fn] = pv
                field_changes += 1

        # ── 3. Remaining xpath absolute fix ───────────────────────────────────
        for fn, pv in prov.items():
            if not isinstance(pv, dict): continue
            xpath = pv.get('xpath', '') or ''
            css   = pv.get('css_selector', '') or ''
            if re.search(r'/(html|body)\[', xpath) or xpath.startswith('/body/'):
                if css and re.search(r'(#[\w-]+|\[data-|\.[\w-]+)', css):
                    # Convert css to xpath approx
                    result = css.strip()
                    result = re.sub(r"\[([^\]='\s]+)='([^']+)'\]", r"[@\1='\2']", result)
                    result = re.sub(r'(\w+)#([\w-]+)', r'\1[@id="\2"]', result)
                    result = re.sub(r'\.([\w-]+)', r'[contains(@class,"\1")]', result)
                    result = re.sub(r':nth-of-type\((\d+)\)', r'[\1]', result)
                    result = re.sub(r':nth-child\((\d+)\)', r'[\1]', result)
                    result = result.replace(' > ', '/').replace('  ', ' ')
                    result = re.sub(r' +', '//', result)
                    if not result.startswith('/'):
                        result = '//' + result
                    if '/html' not in result:
                        pv['xpath'] = result
                        xpath_changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = field_changes + date_changes + xpath_changes
    if total > 0:
        print('%-58s  fields=%d dates=%d xpath=%d' % (fname, field_changes, date_changes, xpath_changes))

print('\n--- Verification ---')
# Check remaining non-canonical field names
remaining = {}
for fname in files:
    with open(os.path.join(GOLD_DIR, fname), 'r', encoding='utf-8') as f:
        data = json.load(f)
    for rec in data.get('records', []):
        for fn in rec.get('fields', {}).keys():
            if fn in CANON and fn not in KEEP_AS_IS:
                remaining.setdefault(fn, set()).add(fname[:20])

if remaining:
    print('Still non-canonical:')
    for fn, files_set in sorted(remaining.items()):
        print('  %s in %s' % (fn, ', '.join(sorted(files_set))))
else:
    print('All field names are canonical!')

print('Done.')
