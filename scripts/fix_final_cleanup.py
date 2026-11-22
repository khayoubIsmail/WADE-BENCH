"""
fix_final_cleanup.py
Two fixes:
  1. Where css_selector == css_selector_absolute (both are the full nth-of-type path),
     set xpath = xpath_absolute (for consistency/uniqueness)
  2. For ONTHEMARKET/REALESTATE.CO.NZ where css_selector_absolute is None but
     css_selector still matches multiple elements, compute absolute path from HTML
     and then make css_selector unique using that prefix.
"""

import json, os, re
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


def normalize_text(t):
    return re.sub(r'\s+', ' ', t or '').strip()


def count_matches(soup, sel):
    try:
        return len(soup.select(sel))
    except Exception:
        return -1


def extract_unique_prefix(css_absolute, soup):
    if not css_absolute: return None, None
    parts = [p.strip() for p in css_absolute.split('>')]
    accumulated = ''
    for i, part in enumerate(parts):
        accumulated = (accumulated + ' > ' + part).strip(' > ')
        try:
            n = len(soup.select(accumulated))
        except Exception:
            continue
        if n == 1:
            remaining = ' > '.join(parts[i+1:]).strip()
            return accumulated, remaining
    return None, None


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get('records', [])
    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    soup = None

    changes = 0
    for rec in records:
        prov = rec.get('provenance', {})
        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue

            css = pv.get('css_selector', '')
            css_abs = pv.get('css_selector_absolute')
            xpath = pv.get('xpath', '')
            xpath_abs = pv.get('xpath_absolute', '')

            # Fix 1: xpath still generic but css_selector is now fully absolute (nth-of-type)
            # When css_selector == css_selector_absolute, xpath should == xpath_absolute
            if css and css_abs and css == css_abs and xpath != xpath_abs and xpath_abs:
                pv['xpath'] = xpath_abs
                changes += 1
                continue

            # Fix 1b: css_selector contains nth-of-type (fully specific) but xpath still generic
            if css and 'nth-of-type' in css and xpath and xpath_abs and xpath != xpath_abs:
                # Only if xpath is still the generic ancestor form
                if '//div[@id=' in xpath or 'contains(@class' in xpath:
                    pv['xpath'] = xpath_abs
                    changes += 1
                    continue

            # Fix 2: css_selector_absolute is None and css still matches multiple elements
            if css_abs is None and css:
                if not os.path.exists(html_path):
                    continue
                if soup is None:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')

                n = count_matches(soup, css)
                if n <= 1:
                    continue

                text_quote = pv.get('text_quote')
                tq = normalize_text(text_quote) if text_quote else None

                # Find the matching element
                try:
                    elements = soup.select(css)
                except Exception:
                    continue

                target = None
                for el in elements:
                    if tq and tq in normalize_text(el.get_text()):
                        target = el
                        break
                if not target and elements:
                    target = elements[0]

                if not target:
                    continue

                new_css_abs = get_css_abs(target)
                new_xpath_abs = get_xpath_abs(target)

                if new_css_abs:
                    pv['css_selector_absolute'] = new_css_abs
                if new_xpath_abs:
                    pv['xpath_absolute'] = new_xpath_abs

                # Now use the new absolute path to derive a unique css_selector
                prefix, remaining = extract_unique_prefix(new_css_abs, soup)
                if prefix:
                    new_css = (prefix + ' > ' + remaining).strip(' > ') if remaining else prefix
                    if count_matches(soup, new_css) == 1:
                        pv['css_selector'] = new_css
                        # Derive xpath scope
                        m = re.match(r'^(\w+)#([\w-]+)', prefix)
                        if m and xpath:
                            xpath_scope = "//%s[@id='%s']" % (m.group(1), m.group(2))
                            inner = xpath.lstrip('/')
                            pv['xpath'] = xpath_scope + '//' + inner if inner else xpath_scope
                        else:
                            pv['xpath'] = new_xpath_abs or xpath or None
                        changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

# Final check
print('\n--- Final uniqueness check ---')
total = 0
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
    issues = 0
    for rec in records[:2]:
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '')
            if css:
                n = count_matches(soup, css)
                if n > 1:
                    issues += 1
    status = 'OK' if issues == 0 else ('%d non-unique' % issues)
    print('  %-60s  %s' % (fname, status))
    total += issues

print('\nTotal remaining: %d' % total)
print('Done.')
