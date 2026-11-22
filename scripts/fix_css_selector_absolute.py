"""
fix_css_selector_absolute.py
For every provenance entry where css_selector_absolute is null but css_selector exists,
re-parse the corresponding HTML, find the nth matching element (nth = record index),
and compute css_selector_absolute from that element.
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def get_css_selector_absolute(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.get('id'):
            path.insert(0, el.name + '#' + el['id'])
            break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        if nth > 1 or el.find_next_siblings(el.name):
            path.insert(0, '%s:nth-of-type(%d)' % (el.name, nth))
        else:
            path.insert(0, el.name)
        el = el.parent
    return ' > '.join(path) if path else None


def css_to_bs4_selector(css):
    """Convert a simple CSS selector string to a BeautifulSoup find_all call args."""
    css = css.strip()
    # Handle [attr*='val'], [attr='val'], tag.class, tag[attr='val']
    # We'll use soup.select() for all of them
    return css


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snap_id = data.get('snapshot_id', '')
    snap_folder = os.path.join(SNAP_DIR, snap_id)
    html_path = os.path.join(snap_folder, 'page.html')

    if not os.path.exists(html_path):
        print('SKIP (no HTML): %s' % fname)
        continue

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Cache of CSS selector -> list of matched elements (in DOM order)
    selector_cache = {}
    changes = 0

    records = data.get('records', [])
    for rec_idx, rec in enumerate(records):
        prov = rec.get('provenance', {})

        for field_name, prov_val in prov.items():
            if not isinstance(prov_val, dict):
                continue
            if prov_val.get('css_selector_absolute') is not None:
                continue  # already set

            css = prov_val.get('css_selector')
            if not css or 'nth-of-type' in css:
                # Skip if no stable selector or it's already absolute
                continue

            # Try to select elements using this CSS
            try:
                if css not in selector_cache:
                    matched = soup.select(css)
                    selector_cache[css] = matched
                elements = selector_cache[css]

                # Pick the nth element corresponding to this record
                el = elements[rec_idx] if rec_idx < len(elements) else None
                if el:
                    abs_css = get_css_selector_absolute(el)
                    prov_val['css_selector_absolute'] = abs_css
                    changes += 1
            except Exception as e:
                pass  # skip unparseable selectors

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  css_abs_fixed=%d' % (fname, changes))

print('\nDone.')
