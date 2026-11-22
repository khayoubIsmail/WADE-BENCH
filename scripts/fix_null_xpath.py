"""
fix_null_xpath.py
Fills in null `xpath` values in provenance by:
  1. Converting css_selector to stable XPath using improved converter
  2. Fallback: deriving stable xpath from element found via css_selector_absolute
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def css_part_to_xpath(part):
    """Convert a single CSS selector part (no combinators) to XPath."""
    part = part.strip()
    if not part:
        return None

    # [attr='val'] or [attr*='val']  standalone
    m = re.match(r"^\[([^=\]]+)([*~|^$]?=)'([^']+)'\]$", part)
    if m:
        attr, op, val = m.group(1), m.group(2), m.group(3)
        if op == '*':
            return "*[contains(@%s,'%s')]" % (attr, val)
        return "*[@%s='%s']" % (attr, val)

    # tag only
    tag = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)$', part)
    if tag:
        return tag.group(1)

    # tag.class
    m = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)\.([^\[:\s]+)$', part)
    if m:
        return "%s[contains(@class,'%s')]" % (m.group(1), m.group(2))

    # .class only
    m = re.match(r'^\.([^\[:\s]+)$', part)
    if m:
        return "*[contains(@class,'%s')]" % m.group(1)

    # tag#id
    m = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)#([^\[:\s]+)$', part)
    if m:
        return "%s[@id='%s']" % (m.group(1), m.group(2))

    # tag[attr='val']
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9]*)\[([^=\]]+)([*~|^$]?=)'([^']+)'\]$", part)
    if m:
        tag2, attr, op, val = m.group(1), m.group(2), m.group(3), m.group(4)
        if op == '*':
            return "%s[contains(@%s,'%s')]" % (tag2, attr, val)
        return "%s[@%s='%s']" % (tag2, attr, val)

    # tag[attr*='val'] (no quotes — some files omit quotes)
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9]*)\[([^=\]]+)\*=([^\]]+)\]$", part)
    if m:
        return "%s[contains(@%s,'%s')]" % (m.group(1), m.group(2), m.group(3))

    return None  # can't convert


def css_to_xpath(css):
    """Convert a full CSS selector (possibly with > combinators) to XPath."""
    css = css.strip()
    # Split on ' > ' or ' ' (child / descendant combinators)
    parts = re.split(r'\s*>\s*', css)
    xpath_parts = []
    for part in parts:
        xp = css_part_to_xpath(part)
        if not xp:
            return None
        xpath_parts.append(xp)

    if not xpath_parts:
        return None

    # First part uses // (descendant), rest use / (child)
    return '//' + '/'.join(xpath_parts)


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


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    soup = None
    selector_cache = {}

    changes = 0
    for rec_idx, rec in enumerate(data.get('records', [])):
        prov = rec.get('provenance', {})
        for field_name, pv in prov.items():
            if not isinstance(pv, dict):
                continue
            if pv.get('xpath') is not None:
                continue  # already set

            css = pv.get('css_selector', '')

            # Try CSS → XPath conversion first
            if css and 'nth-of-type' not in css:
                xpath = css_to_xpath(css)
                if xpath:
                    pv['xpath'] = xpath
                    changes += 1
                    continue

            # Fallback: load HTML and compute from element
            if not soup and os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

            if soup and css:
                try:
                    if css not in selector_cache:
                        selector_cache[css] = soup.select(css)
                    elements = selector_cache[css]
                    el = elements[rec_idx] if rec_idx < len(elements) else None
                    if el:
                        pv['xpath'] = get_xpath_absolute(el)
                        changes += 1
                except Exception:
                    pass

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  xpath_fixed=%d' % (fname, changes))

print('\nDone.')
