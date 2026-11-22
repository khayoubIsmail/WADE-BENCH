"""
fix_apartments_css_selectors.py
Updates css_selector and xpath for Apartments fields that use generic div.val
to use the semantic li class selector instead: li.sq.-ft. > div.val, etc.
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


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

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

    changes = 0
    records = data.get('records', [])

    for rec_idx, rec in enumerate(records):
        prov = rec.get('provenance', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue

            css = pv.get('css_selector', '')
            text_quote = pv.get('text_quote')

            # Only fix generic selectors that match too many elements
            if not css or 'nth-of-type' in css:
                continue

            try:
                matched = soup.select(css)
            except Exception:
                continue

            if len(matched) <= 1:
                continue  # already specific enough

            # Try to find a more specific selector by checking parent li classes
            # or sibling labels

            tq = normalize_text(text_quote) if text_quote else None

            # Find the actual target element
            target_el = None
            for el in matched:
                if tq and tq in normalize_text(el.get_text()):
                    target_el = el
                    break

            if not target_el:
                if rec_idx < len(matched):
                    target_el = matched[rec_idx]
                else:
                    continue

            # Check if parent li has a semantic class
            parent_li = target_el.find_parent('li')
            if parent_li and parent_li.get('class'):
                li_classes = '.'.join(parent_li.get('class', []))
                # Build a specific stable selector using li class
                new_css = 'li.%s > %s' % (li_classes, css.split('>')[-1].strip())

                # Verify this selector matches something
                try:
                    test_match = soup.select(new_css)
                except Exception:
                    test_match = []

                if test_match:
                    # Convert li class to xpath
                    li_xpath_part = ' and '.join("contains(@class,'%s')" % c for c in parent_li.get('class', []))
                    new_xpath = "//li[%s]/%s" % (li_xpath_part, css.split('>')[-1].strip().replace('.', "[contains(@class,'").replace(' ', '') + "')]") if '.' in css.split('>')[-1] else "//li[%s]/%s" % (li_xpath_part, css.split('>')[-1].strip())

                    # Simpler: convert the target element's CSS to stable xpath
                    inner_el_tag = css.split('>')[-1].strip()
                    inner_tag = re.match(r'^(\w+)', inner_el_tag)
                    if inner_tag:
                        inner_class = re.search(r'\.(\S+)', inner_el_tag)
                        if inner_class:
                            new_xpath = "//li[%s]/%s[contains(@class,'%s')]" % (li_xpath_part, inner_tag.group(1), inner_class.group(1))
                        else:
                            new_xpath = "//li[%s]/%s" % (li_xpath_part, inner_tag.group(1))

                    if pv.get('css_selector') != new_css or pv.get('xpath') != new_xpath:
                        pv['css_selector'] = new_css
                        pv['xpath'] = new_xpath
                        # Recompute absolute paths from actual target element
                        pv['css_selector_absolute'] = get_css_selector_absolute(target_el)
                        pv['xpath_absolute'] = get_xpath_absolute(target_el)
                        changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  refined=%d' % (fname, changes))

print('\nDone.')
