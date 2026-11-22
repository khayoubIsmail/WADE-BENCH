"""
fix_numeric_normalized.py
Converts normalized string values to proper JSON int/float for known numeric fields.
ID-like fields (MLS numbers, APN, phone numbers) are kept as strings.
"""

import json, os, re

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

# Fields that must have integer normalized values
INTEGER_FIELDS = {
    'bedrooms', 'bathrooms', 'beds', 'baths', 'full_baths', 'total_baths',
    'partial_baths', 'rooms', 'garages', 'parking', 'floors', 'year_built',
    'stories', 'units', 'nb_rooms', 'pieces', 'floor_number',
    # Capitalized variants from APARTMENTS
    'Beds', 'Full_Baths', 'Total_Baths', 'Partial_Baths', 'Baths',
    'Car_Garage', 'bedrooms_count', 'bathrooms_count',
}

# Fields that must have float normalized values
FLOAT_FIELDS = {
    'floor_area', 'lot_size', 'land_area', 'surface', 'surface_habitable',
    'price_per_sqft', 'price_per_m2', 'prix_par_m2', 'rating',
    'price_per_square_meter', 'area',
}

# Fields that look numeric but are IDs — keep as string
STRING_ID_FIELDS = {
    'MLS_Number', 'MLS_number', 'MLS_ID', 'MLS_number',
    'APN', 'BER_No', 'Reference', 'listing_agent_phone',
    'finnkode', 'property_id', 'listing_id', 'ref',
}


def try_int(s):
    try:
        return int(str(s).replace(',', '').replace(' ', '').strip())
    except Exception:
        return None


def try_float(s):
    try:
        return float(str(s).replace(',', '').replace(' ', '').strip())
    except Exception:
        return None


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

total_int = 0
total_float = 0

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changes = 0
    for rec in data.get('records', []):
        fields = rec.get('fields', {})
        for fn, fv in fields.items():
            if not isinstance(fv, dict):
                continue
            norm = fv.get('normalized')
            if not isinstance(norm, str):
                continue  # already typed or null

            fn_lower = fn.lower()

            if fn in STRING_ID_FIELDS:
                continue  # keep as string

            if fn in INTEGER_FIELDS or fn_lower in {f.lower() for f in INTEGER_FIELDS}:
                result = try_int(norm)
                if result is not None:
                    fv['normalized'] = result
                    changes += 1
                    total_int += 1

            elif fn in FLOAT_FIELDS or fn_lower in {f.lower() for f in FLOAT_FIELDS}:
                result = try_float(norm)
                if result is not None:
                    fv['normalized'] = result
                    changes += 1
                    total_float += 1

            else:
                # Unknown field — try to auto-detect if it's a pure integer
                # (no decimal, no special chars other than commas, not an ID)
                clean = norm.replace(',', '').strip()
                if re.fullmatch(r'\d+', clean) and len(clean) <= 6:
                    # Short integer (not a long ID like MLS)
                    result = try_int(norm)
                    if result is not None:
                        fv['normalized'] = result
                        changes += 1
                        total_int += 1
                elif re.fullmatch(r'\d+\.\d+', clean):
                    result = try_float(norm)
                    if result is not None:
                        fv['normalized'] = result
                        changes += 1
                        total_float += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  int/float=%d' % (fname, changes))

print('\nTotal int conversions: %d | float conversions: %d' % (total_int, total_float))
print('Done.')
