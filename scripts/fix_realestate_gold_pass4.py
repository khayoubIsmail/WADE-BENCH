"""
fix_realestate_gold_pass4.py
Applies lowercase canonical normalization per guideline §1.6:
  property_type, status, tenure, ownership_type, furnish_type, sale_type → lowercase
"""

import json, os

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

# Category fields whose normalized value should be lowercase canonical
CATEGORY_FIELDS = {
    'property_type', 'status', 'tenure', 'ownership_type',
    'furnish_type', 'sale_type', 'Selling_Type', 'type'
}

files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changes = 0
    for rec in data.get('records', []):
        fields = rec.get('fields', {})
        for field_name, field_val in fields.items():
            if field_name in CATEGORY_FIELDS and isinstance(field_val, dict):
                norm = field_val.get('normalized')
                if isinstance(norm, str) and norm != norm.lower():
                    field_val['normalized'] = norm.lower()
                    changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print("%-60s  changes=%d" % (fname, changes))

print("\nDone.")
