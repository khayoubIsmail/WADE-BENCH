"""
fix_provenance_by_text_quote.py

Deep provenance verification and correction:
For every provenance entry with a text_quote, find the actual DOM element
whose text matches the text_quote, then recompute css_selector_absolute
and xpath_absolute from that element.

Strategy:
  1. Find ALL elements matching css_selector in the HTML
  2. Among them, pick the one whose text contains text_quote
  3. For disambiguation (multiple matches), prefer the one closest to
     the expected record position in the DOM
  4. Recompute absolute paths from the matched element
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


def get_xpath_absolute(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.name == 'html':
            path.insert(0, '/html')
            break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        path.insert(0, '%s[%d]' % (el.name, nth))
        el = el.parent
    return '/' + '/'.join(path) if path else None


def normalize_text(t):
    return re.sub(r'\s+', ' ', t or '').strip()


def find_element_by_text_quote(elements, text_quote, rec_idx, total_recs):
    """
    Given a list of candidate elements and the expected text_quote,
    find the best matching element.
    Priority:
      1. Exact text match (normalized)
      2. Substring match (text_quote in element text)
      3. Fall back to rec_idx-based selection
    """
    if not text_quote:
        if rec_idx < len(elements):
            return elements[rec_idx]
        return None

    tq = normalize_text(text_quote)

    # Try exact match first
    exact = [el for el in elements if normalize_text(el.get_text()) == tq]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        # Multiple exact matches — pick nth based on record position
        step = len(exact) // total_recs if total_recs > 0 else 1
        idx = min(rec_idx * step, len(exact) - 1) if step > 0 else rec_idx
        return exact[min(rec_idx, len(exact) - 1)]

    # Try substring match
    partial = [el for el in elements if tq in normalize_text(el.get_text())]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        return partial[min(rec_idx, len(partial) - 1)]

    # Fall back to index
    if rec_idx < len(elements):
        return elements[rec_idx]
    return None


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

total_fixed = 0

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')

    if not os.path.exists(html_path):
        continue

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    selector_cache = {}
    records = data.get('records', [])
    total_recs = len(records)
    changes = 0

    for rec_idx, rec in enumerate(records):
        prov = rec.get('provenance', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict):
                continue

            css = pv.get('css_selector', '')
            text_quote = pv.get('text_quote')

            if not css or 'nth-of-type' in css:
                continue  # skip absolute CSS selectors (already specific)

            # Get all elements matching the CSS selector
            try:
                if css not in selector_cache:
                    selector_cache[css] = soup.select(css)
                elements = selector_cache[css]
            except Exception:
                continue

            if not elements:
                continue

            # Find the correct element using text_quote
            el = find_element_by_text_quote(elements, text_quote, rec_idx, total_recs)

            if not el:
                continue

            new_css_abs = get_css_selector_absolute(el)
            new_xpath_abs = get_xpath_absolute(el)

            # Check if the absolute paths changed (i.e., were wrong)
            old_css_abs = pv.get('css_selector_absolute')
            old_xpath_abs = pv.get('xpath_absolute')

            if new_css_abs != old_css_abs or new_xpath_abs != old_xpath_abs:
                pv['css_selector_absolute'] = new_css_abs
                pv['xpath_absolute'] = new_xpath_abs
                changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total_fixed += changes
    if changes > 0:
        print('%-60s  corrected=%d' % (fname, changes))

print('\nTotal corrected: %d' % total_fixed)
print('Done.')
