"""
fix_price_normalized.py
Fixes:
  1. All monetary fields: normalized plain-number → {amount, currency: {name, code, symbol}}
  2. Remaining field name renames: Bedrooms, Price_per_sq.__ft._, Monthly_HOA_dues, etc.
"""

import json, os, re

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

# ─── Currency detection ────────────────────────────────────────────────────────
CURRENCIES = {
    'NZ$': ('NZD', 'New Zealand dollar', 'NZ$'),
    'AU$': ('AUD', 'Australian dollar', 'AU$'),
    'CA$': ('CAD', 'Canadian dollar', 'CA$'),
    '$':   ('USD', 'US dollar', '$'),
    '€':   ('EUR', 'Euro', '€'),
    '\u20ac': ('EUR', 'Euro', '€'),  # unicode euro
    '£':   ('GBP', 'British pound', '£'),
    'NOK': ('NOK', 'Norwegian krone', 'kr'),
    'kr':  ('NOK', 'Norwegian krone', 'kr'),
    'MAD': ('MAD', 'Moroccan dirham', 'MAD'),
    'DH':  ('MAD', 'Moroccan dirham', 'DH'),
    '\u062f\u0631\u0647\u0645': ('MAD', 'Moroccan dirham', 'درهم'),  # درهم
    'AED': ('AED', 'UAE dirham', 'AED'),
    'IRL': ('EUR', 'Euro', '€'),
}

SITE_CURRENCY = {
    'FINN':          ('NOK', 'Norwegian krone', 'kr'),
    'LEBONCOIN':     ('EUR', 'Euro', '€'),
    'DAFT':          ('EUR', 'Euro', '€'),
    'RIGHTMOVE':     ('GBP', 'British pound', '£'),
    'ONTHEMARKET':   ('GBP', 'British pound', '£'),
    'REALESTATE.CO': ('NZD', 'New Zealand dollar', 'NZ$'),
    'REDFIN':        ('USD', 'US dollar', '$'),
    'APARTMENTS':    ('USD', 'US dollar', '$'),
    'CENTURY_21':    ('USD', 'US dollar', '$'),
    'MAROC':         ('MAD', 'Moroccan dirham', 'MAD'),
}

# Monetary field name keywords
MONETARY_KEYWORDS = re.compile(
    r'price|cost|fee|dues|rent|hoa|monthly|debt|wealth|assessment|'
    r'frais|mensualit|loyer|prix', re.I
)

# Additional field renames not caught before
EXTRA_CANON = {
    'Bedrooms': 'bedrooms',
    'Bathrooms': 'bathrooms',
    'Price_per_sq.__ft._': 'price_per_sqft',
    'Monthly_HOA_dues': 'monthly_hoa_dues',
    'Status': 'status',
    'Total_price': 'total_price',
    'Price_Assessment': 'price_assessment',
    'Price_per_m\u00b2': 'price_per_m2',
    'Price_per_m²': 'price_per_m2',
    'Joint_debt': 'joint_debt',
    'Common_cost_mn': 'common_cost_monthly',
    'Joint_wealth': 'joint_wealth',
    'Selling_Type': 'sale_type',
    'Type': 'property_type',
}


def detect_currency(value_str, fname):
    """Detect currency from value string, fallback to site-based detection."""
    s = str(value_str)
    # Try symbol-based detection (order matters: NZ$ before $)
    for sym, cinfo in CURRENCIES.items():
        if sym in s:
            return cinfo
    # Fallback to site-based
    for site_key, cinfo in SITE_CURRENCY.items():
        if site_key in fname:
            return cinfo
    return None


def parse_amount(value_str):
    """Extract numeric amount from value string."""
    s = str(value_str)
    # Remove thousands separators (comma, space, nbsp, thin-space)
    s = re.sub(r'[\s\u00a0\u202f,]', '', s)
    # Extract first number
    m = re.search(r'[\d]+(?:\.\d+)?', s)
    if m:
        v = float(m.group())
        return int(v) if v == int(v) else v
    return None


def make_currency_obj(amount, currency_info):
    code, name, symbol = currency_info
    return {
        "amount": float(amount),
        "currency": {
            "name": name,
            "code": code,
            "symbol": symbol
        }
    }


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    price_changes = 0
    rename_changes = 0

    for rec in data.get('records', []):
        fields = rec.get('fields', {})
        prov   = rec.get('provenance', {})

        # ── 1. Additional field renames ───────────────────────────────────────
        for old_fn, new_fn in list(EXTRA_CANON.items()):
            if old_fn in fields:
                if new_fn not in fields:
                    fields[new_fn] = fields.pop(old_fn)
                    if old_fn in prov:
                        prov[new_fn] = prov.pop(old_fn)
                    rename_changes += 1
                else:
                    # Canonical already exists — delete non-canonical
                    del fields[old_fn]
                    if old_fn in prov:
                        del prov[old_fn]
                    rename_changes += 1

        # ── 2. Monetary normalization ─────────────────────────────────────────
        for fn, fv in fields.items():
            if not isinstance(fv, dict):
                continue
            norm = fv.get('normalized')
            val  = fv.get('value', '')

            # Skip already-structured
            if isinstance(norm, dict):
                continue

            # Only process if field name looks monetary AND norm is a number
            if not isinstance(norm, (int, float)):
                continue
            if not MONETARY_KEYWORDS.search(fn):
                continue

            # Detect currency from value
            cinfo = detect_currency(val, fname)
            if not cinfo:
                continue

            # Build structured normalized
            amount = parse_amount(val) if parse_amount(val) is not None else float(norm)
            fv['normalized'] = make_currency_obj(amount, cinfo)
            price_changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = price_changes + rename_changes
    if total > 0:
        print('%-58s  renames=%d prices=%d' % (fname, rename_changes, price_changes))

print('\n--- Verification ---')
issues = 0
for fname in files:
    with open(os.path.join(GOLD_DIR, fname), 'r', encoding='utf-8') as f:
        data = json.load(f)
    for rec in data.get('records', []):
        for fn, fv in rec.get('fields', {}).items():
            if not isinstance(fv, dict): continue
            norm = fv.get('normalized')
            val  = str(fv.get('value', ''))
            if isinstance(norm, (int, float)) and MONETARY_KEYWORDS.search(fn):
                # Still plain number for monetary field?
                import re as _re
                if _re.search(r'[\$\£\€]|NOK|\bkr\b', val):
                    print('  STILL PLAIN: %-20s | %-25s | val=%r norm=%r' % (
                        fname[:20], fn, val[:20], norm))
                    issues += 1

if issues == 0:
    print('All monetary fields have structured normalized!')
else:
    print('%d issues remain.' % issues)

print()
# Check example
with open(os.path.join(GOLD_DIR, 'WBV1_REAL_CENTURY_21_002_DETAIL.json'), 'r', encoding='utf-8') as f:
    d = json.load(f)
rec = d['records'][0]
for fn in ['price', 'price_per_sqft', 'monthly_hoa_dues', 'bedrooms', 'Bedrooms']:
    if fn in rec['fields']:
        print('%s: %s' % (fn, json.dumps(rec['fields'][fn], ensure_ascii=False)[:80]))
print('Done.')
