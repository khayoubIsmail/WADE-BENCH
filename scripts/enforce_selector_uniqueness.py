"""
enforce_selector_uniqueness.py
Checks all 4 selectors in each provenance entry for uniqueness on the page.
For any non-unique css_selector or xpath, scopes it to the record's listing anchor.
For xpath_absolute and css_selector_absolute, these should already be unique (absolute paths).
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def count_matches(soup, selector):
    try:
        return len(soup.select(selector))
    except Exception:
        return -1


def find_unique_anchor_for_record(rec):
    """Extract unique href fragment from listing_url."""
    url = rec.get('fields', {}).get('listing_url', {}).get('value', '')
    if not url:
        return None, None
    pid = re.search(r'pid_\d+', url)
    if pid:
        frag = pid.group(0)
        return "a[href*='%s']" % frag, "//a[contains(@href,'%s')]" % frag
    # Try last 2 path segments as unique slug
    m = re.search(r'/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)/?$', url)
    if m:
        frag = m.group(1)
        return "a[href*='%s']" % frag, "//a[contains(@href,'%s')]" % frag
    return None, None


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get('records', [])
    if len(records) <= 1:
        continue  # detail pages: single record, selectors are already unique

    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    if not os.path.exists(html_path):
        continue

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    changes = 0
    for rec in records:
        prov = rec.get('provenance', {})
        css_anchor, xpath_anchor = find_unique_anchor_for_record(rec)

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue
            if field_name == 'listing_url': continue

            # Fix css_selector if not unique
            css = pv.get('css_selector', '')
            if css and 'nth-of-type' not in css:
                n = count_matches(soup, css)
                if n > 1 and css_anchor:
                    scoped = css_anchor + ' ' + css
                    n_scoped = count_matches(soup, scoped)
                    if n_scoped <= n:  # scoping helped
                        pv['css_selector'] = scoped
                        changes += 1

            # Fix xpath if not unique (check by counting //)
            # We can't easily count xpath matches with bs4, but we scope it to match css fix
            xpath = pv.get('xpath', '')
            if xpath and xpath_anchor and css_anchor in pv.get('css_selector', ''):
                # css was scoped, scope xpath too if not already
                if xpath_anchor not in xpath:
                    # Combine: xpath_anchor + descendant xpath
                    inner = xpath.lstrip('/')
                    # Remove leading /html... absolute prefix if present
                    if not inner.startswith('/'):
                        pv['xpath'] = xpath_anchor + '//' + inner
                    changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  enforced=%d' % (fname, changes))

# Final report: count any remaining non-unique css_selectors
print('\n--- Remaining non-unique css_selectors (>1 match) ---')
for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = data.get('records', [])
    if len(records) <= 1:
        continue
    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    if not os.path.exists(html_path):
        continue
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    non_unique = set()
    for rec in records:
        for field_name, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '')
            if css:
                n = count_matches(soup, css)
                if n > 1:
                    non_unique.add((field_name, css, n))

    if non_unique:
        print('%s:' % fname)
        for fn, css, n in sorted(non_unique):
            print('  [%d matches] %s: %s' % (n, fn, css[:80]))

print('\nDone.')
