"""Fix double-quote attribute selectors to use single quotes."""
import json, os

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

fixes = 0
for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for rec in data.get('records', []):
        prov = rec.get('provenance', {})
        for field_name, pv in prov.items():
            if not isinstance(pv, dict):
                continue
            for sel_key in ['css_selector', 'css_selector_absolute', 'xpath', 'xpath_absolute']:
                val = pv.get(sel_key)
                if not val or not isinstance(val, str):
                    continue
                if '"' in val:
                    pv[sel_key] = val.replace('"', "'")
                    fixes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

print('Fixed %d double-quote selectors to single-quote' % fixes)
