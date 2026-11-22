"""
fix_remaining_nonunique.py
For files still having non-unique css_selectors:
  - Extract a unique card scope from css_selector_absolute
  - Use it to make css_selector and xpath unique
  - Strategy: find the first element in css_selector_absolute that has an id
    OR the first nth-of-type that uniquely scopes to the card
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


def extract_unique_prefix_from_abs(css_absolute, soup):
    """
    Walk the css_selector_absolute path from left to right,
    find the shortest prefix that uniquely identifies one element on the page.
    Returns (prefix_css, remaining_css) or (None, None).
    """
    if not css_absolute:
        return None, None

    parts = [p.strip() for p in css_absolute.split('>')]
    accumulated = ''
    for i, part in enumerate(parts):
        if accumulated:
            accumulated += ' > ' + part
        else:
            accumulated = part
        try:
            n = len(soup.select(accumulated))
        except Exception:
            continue
        if n == 1:
            remaining = ' > '.join(parts[i+1:]).strip()
            return accumulated, remaining
    return None, None


def css_scope_to_xpath_scope(css_scope):
    """Convert a CSS scope like div#snapshot-1 to XPath like //div[@id='snapshot-1']"""
    if not css_scope:
        return None
    # Handle id: tag#id
    m = re.match(r'^(\w+)#([\w-]+)$', css_scope.strip())
    if m:
        return "//%s[@id='%s']" % (m.group(1), m.group(2))
    # Handle nth-of-type chain — just return None, we'll use css_abs for xpath too
    return None


def build_scoped_xpath(xpath_scope, original_xpath):
    if not xpath_scope or not original_xpath:
        return original_xpath
    # Strip existing scope prefixes
    inner = re.sub(r'^//\w+\[.*?\]//', '//', original_xpath)
    inner = re.sub(r'^//\w+\[@id=\'[^\']+\'\]', '', inner)
    if not inner.startswith('/'):
        inner = '//' + inner
    return xpath_scope + inner


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

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

    changes = 0
    for rec in records:
        prov = rec.get('provenance', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict):
                continue

            css = pv.get('css_selector', '')
            xpath = pv.get('xpath', '')
            css_abs = pv.get('css_selector_absolute', '')

            if not css:
                continue

            # Check if still non-unique
            n = count_matches(soup, css)
            if n <= 1:
                continue  # already unique

            # Get unique prefix from css_selector_absolute
            prefix, remaining = extract_unique_prefix_from_abs(css_abs, soup)

            if not prefix:
                continue

            # Build new scoped css_selector
            if remaining:
                # Use: prefix + remaining (which is the specific inner element)
                new_css = prefix + ' > ' + remaining
            else:
                # Prefix IS the absolute path — use as-is
                new_css = prefix

            # Verify
            n_new = count_matches(soup, new_css)

            if n_new == 1:
                pv['css_selector'] = new_css
                # Build scoped xpath
                xpath_scope = css_scope_to_xpath_scope(prefix)
                if xpath_scope:
                    new_xpath = build_scoped_xpath(xpath_scope, xpath)
                    if new_xpath:
                        pv['xpath'] = new_xpath
                changes += 1
            elif n_new > 1 and n_new < n:
                # Partial improvement — still better
                pv['css_selector'] = new_css
                changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

# Final uniqueness report
print('\n--- Final uniqueness check ---')
total_issues = 0
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

    issues = []
    for rec in records[:2]:
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '')
            if css:
                n = count_matches(soup, css)
                if n > 1:
                    issues.append((fn, n, css[:70]))

    if issues:
        print('%s: %d non-unique' % (fname, len(issues)))
        for fn, n, css in issues[:3]:
            print('  [%d] %s: %s' % (n, fn, css))
        total_issues += len(issues)
    else:
        print('%s: OK' % fname)

print('\nTotal remaining issues: %d' % total_issues)
print('Done.')
