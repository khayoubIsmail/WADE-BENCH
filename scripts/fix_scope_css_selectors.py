"""
fix_scope_css_selectors.py
Makes css_selector globally unique on listing pages by scoping it
to the specific listing card using href*='pid_XXXXX'.

For each record, find the unique anchor/container for that listing,
then prefix all field css_selectors with that unique scope.
"""

import json, re, os
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def get_css_abs(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.get('id'):
            path.insert(0, el.name + '#' + el['id']); break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        if nth > 1 or el.find_next_siblings(el.name):
            path.insert(0, '%s:nth-of-type(%d)' % (el.name, nth))
        else:
            path.insert(0, el.name)
        el = el.parent
    return ' > '.join(path) if path else None


def get_xpath_abs(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.name == 'html':
            path.insert(0, '/html'); break
        siblings = el.find_previous_siblings(el.name)
        nth = len(siblings) + 1
        path.insert(0, '%s[%d]' % (el.name, nth))
        el = el.parent
    return '/' + '/'.join(path) if path else None


def count_matches(soup, selector):
    try:
        return len(soup.select(selector))
    except Exception:
        return 0


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Only apply to LISTING files (multiple records)
    records = data.get('records', [])
    if len(records) <= 1:
        continue

    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    if not os.path.exists(html_path):
        continue

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    changes = 0
    for rec_idx, rec in enumerate(records):
        fields = rec.get('fields', {})
        prov = rec.get('provenance', {})

        # Get the unique scope for this record
        # Try listing_url -> extract pid or unique href fragment
        scope_prefix = None
        xpath_scope_prefix = None
        listing_url_val = fields.get('listing_url', {}).get('value', '')

        if listing_url_val:
            # Extract a short unique fragment from URL (pid, property ID, slug)
            pid_m = re.search(r'pid_\d+', listing_url_val)
            slug_m = re.search(r'/([^/]+/[^/]+)/?$', listing_url_val)
            if pid_m:
                unique_frag = pid_m.group(0)
                scope_prefix = 'a[href*="%s"]' % unique_frag
                xpath_scope_prefix = '//a[contains(@href,"%s")]' % unique_frag
            elif slug_m:
                unique_frag = slug_m.group(1)
                scope_prefix = 'a[href*="%s"]' % unique_frag
                xpath_scope_prefix = '//a[contains(@href,"%s")]' % unique_frag

        if not scope_prefix:
            continue

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue
            if field_name == 'listing_url': continue  # already unique

            css = pv.get('css_selector', '')
            if not css or 'nth-of-type' in css:
                continue  # already absolute, skip

            # Check how many the current selector matches
            n_matches = count_matches(soup, css)
            if n_matches <= 1:
                continue  # already unique

            # Try scoping to the listing anchor
            scoped_css = scope_prefix + ' ' + css
            n_scoped = count_matches(soup, scoped_css)

            if n_scoped == 1:
                # Perfect — uniquely scoped
                xpath = pv.get('xpath', '')
                if xpath:
                    # Build scoped xpath
                    scoped_xpath = xpath_scope_prefix + '/' + xpath.lstrip('/')
                else:
                    scoped_xpath = None

                pv['css_selector'] = scoped_css
                if scoped_xpath:
                    pv['xpath'] = scoped_xpath
                changes += 1

            elif n_scoped > 1:
                # Still ambiguous — use scoped + text_quote still disambiguates
                # At least scope it to reduce to per-card level
                pv['css_selector'] = scope_prefix + ' ' + css
                changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  scoped=%d' % (fname, changes))

print('\nDone.')
