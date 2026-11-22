"""
fix_scope_with_snapshot_id.py
Replaces invalid a[href*='pid'] scope prefix in css_selector and xpath
with the correct div#snapshot-N scope derived from css_selector_absolute.
Also uses div[@id='snapshot-N'] scope for xpath.
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def extract_snapshot_id(css_absolute):
    """Extract div#snapshot-N from css_selector_absolute."""
    if not css_absolute:
        return None
    m = re.match(r'^([\w]+#[\w-]+)', css_absolute)
    if m:
        return m.group(1)  # e.g. div#snapshot-0
    return None


def build_scoped_css(snapshot_scope, original_css):
    """Build scoped CSS: div#snapshot-0 li.car-garage > div.val"""
    # Strip any existing bad scope (a[href*=...])
    css = re.sub(r"a\[href\*='[^']+'\]\s*", '', original_css).strip()
    if not css:
        return None
    return snapshot_scope + ' ' + css


def build_scoped_xpath(snapshot_scope, original_xpath):
    """Build scoped xpath: //div[@id='snapshot-0']//li[...]"""
    # Extract the div id from snapshot_scope (e.g. div#snapshot-0)
    m = re.search(r'#([\w-]+)', snapshot_scope)
    if not m:
        return original_xpath
    snap_id = m.group(1)
    tag = snapshot_scope.split('#')[0]

    # Strip existing bad scope
    xpath = re.sub(r"//a\[contains\(@href,'[^']+'\)\]//", '//', original_xpath)
    xpath = re.sub(r"//a\[contains\(@href,'[^']+'\)\]/", '/', original_xpath)

    # Rebuild with correct scope
    inner = xpath.lstrip('/')
    return "//%s[@id='%s']//%s" % (tag, snap_id, inner)


def count_matches(soup, selector):
    try:
        return len(soup.select(selector))
    except Exception:
        return -1


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get('records', [])
    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    if not os.path.exists(html_path):
        continue

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    changes = 0
    for rec in records:
        prov = rec.get('provenance', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue
            if field_name == 'listing_url': continue

            css = pv.get('css_selector', '')
            xpath = pv.get('xpath', '')
            css_abs = pv.get('css_selector_absolute', '')

            # Only fix entries that have invalid a[href*=] scope
            has_bad_scope = "a[href*=" in (css or '')
            # Also fix entries that still match multiple elements (no scope)
            n_matches = count_matches(soup, css) if css and not has_bad_scope else -1

            needs_fix = has_bad_scope or (n_matches > 1 and len(records) > 1)

            if not needs_fix:
                continue

            # Get unique scope from css_selector_absolute
            snap_scope = extract_snapshot_id(css_abs)
            if not snap_scope:
                continue

            # Build new scoped selectors
            new_css = build_scoped_css(snap_scope, css)
            new_xpath = build_scoped_xpath(snap_scope, xpath) if xpath else None

            if new_css:
                n_new = count_matches(soup, new_css)
                if n_new >= 0:
                    pv['css_selector'] = new_css
                    if new_xpath:
                        pv['xpath'] = new_xpath
                    changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

# Verification report
print('\n--- Uniqueness report after fix ---')
for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = data.get('records', [])
    if len(records) <= 1: continue
    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    if not os.path.exists(html_path): continue
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    non_unique = []
    for rec in records[:2]:  # check first 2 records
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '')
            if css:
                n = count_matches(soup, css)
                if n > 1:
                    non_unique.append((fn, n, css[:60]))
    if non_unique:
        print('%s: still non-unique:' % fname)
        for fn, n, css in non_unique[:3]:
            print('  [%d] %s: %s' % (n, fn, css))
    else:
        print('%s: OK' % fname)

print('\nDone.')
