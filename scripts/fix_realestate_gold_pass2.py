"""
fix_realestate_gold_pass2.py
Second pass: fix remaining issues:
  1. FINN_EIENDOM, LEBONCOIN, MAROC_ANNONCES, ONTHEMARKET, REALESTATE.CO.NZ prices 
     where normalized is a plain number, not a currency dict
  2. REDFIN bedrooms where normalized is "4 beds" string -> int
  3. RIGHTMOVE "Reduced yesterday" relative date -> null
"""

import json, os, re

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

CURRENCY_MAP = [
    (r'£',      {'name': 'British pound',     'code': 'GBP', 'symbol': '£'}),
    (r'NZ\$',   {'name': 'New Zealand dollar', 'code': 'NZD', 'symbol': 'NZ$'}),
    (r'\$',     {'name': 'US dollar',          'code': 'USD', 'symbol': '$'}),
    (r'€',      {'name': 'Euro',               'code': 'EUR', 'symbol': '€'}),
    (r'\bkr\b', {'name': 'Norwegian krone',    'code': 'NOK', 'symbol': 'kr'}),
    (r'\bMAD\b',{'name': 'Moroccan dirham',    'code': 'MAD', 'symbol': 'MAD'}),
    (r'\bDH\b', {'name': 'Moroccan dirham',    'code': 'MAD', 'symbol': 'MAD'}),
]

NZD_FILES = {'WBV1_REAL_REALESTATE.CO.NZ_001_LISTING.json', 'WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL.json'}

RELATIVE_PATTERNS = [
    r'\byesterday\b', r'\btoday\b', r'\bjust now\b', r'ago\b',
    r'\d+ day', r'\d+ hour', r'\brecently\b', r'^Reduced yesterday',
]


def detect_currency(value_str, fname):
    if fname in NZD_FILES and '$' in value_str:
        return {'name': 'New Zealand dollar', 'code': 'NZD', 'symbol': 'NZ$'}
    for pattern, info in CURRENCY_MAP:
        if re.search(pattern, value_str):
            return info
    return None


def parse_amount(value_str):
    cleaned = re.sub(r'[^0-9]', '', value_str)
    try:
        return float(cleaned)
    except ValueError:
        return None


def is_relative_date(val):
    if not isinstance(val, str):
        return False
    for p in RELATIVE_PATTERNS:
        if re.search(p, val, re.IGNORECASE):
            return True
    return False


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    counts = {'price': 0, 'bed': 0, 'date': 0}
    records = data.get('records', [])

    for rec in records:
        fields = rec.get('fields', {})

        # Fix price: if normalized is a bare number (int/float), wrap it
        if 'price' in fields:
            pf = fields['price']
            norm = pf.get('normalized')
            value = pf.get('value', '')
            if isinstance(norm, (int, float)) and isinstance(value, str):
                currency = detect_currency(value, fname)
                amount = parse_amount(value)
                if currency and amount is not None:
                    pf['normalized'] = {'amount': amount, 'currency': currency}
                    counts['price'] += 1

        # Fix bedrooms: "4 beds" or "4 bed" -> int
        for bf in ['bedrooms', 'bathrooms']:
            if bf in fields:
                bfv = fields[bf]
                norm = bfv.get('normalized')
                if isinstance(norm, str):
                    m = re.match(r'^(\d+)', norm.strip())
                    if m:
                        bfv['normalized'] = int(m.group(1))
                        counts['bed'] += 1

        # Fix relative dates -> null
        for df in ['published_date', 'listed_datetime']:
            if df in fields:
                dfv = fields[df]
                norm = dfv.get('normalized')
                if is_relative_date(norm):
                    dfv['normalized'] = None
                    counts['date'] += 1
                # Also check value
                val = dfv.get('value')
                if is_relative_date(val) and norm == val:
                    dfv['normalized'] = None
                    counts['date'] += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = sum(counts.values())
    if total > 0:
        print("%-60s  price=%d  bed=%d  date=%d" % (fname, counts['price'], counts['bed'], counts['date']))

print("\nDone.")
