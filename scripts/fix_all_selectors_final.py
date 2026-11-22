"""
fix_all_selectors_final.py
Comprehensive fix for all provenance selectors per WADE-Bench guidelines:

Rules:
  css_selector = stable semantic (NO nth-of-type, prefer data-*, aria-*, IDs, classes)
  css_selector_absolute = full positional backup (nth-of-type chains)
  xpath = stable semantic XPath (parallel to css_selector)
  xpath_absolute = full positional backup

Fixes:
  1. listing_url on detail pages -> link[rel='canonical'] if exists in HTML
  2. images_urls from meta -> meta[property='og:image']
  3. data-test/data-testid attributes -> use as stable selector
  4. css_selector with nth-of-type -> restore semantic using DOM walk
  5. xpath starting with //html/body -> restore to semantic form
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


# ─── Helpers ──────────────────────────────────────────────────────────────────

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


def find_stable_attr_selector(el):
    """Check el and its ancestors for stable data-* or aria attributes."""
    candidate = el
    for _ in range(6):
        if not candidate or not candidate.name:
            break
        for attr in ['data-test', 'data-testid', 'data-tracking', 'data-finn-code',
                     'data-listing-id', 'data-id', 'aria-label', 'data-cy']:
            val = candidate.get(attr)
            if val and not re.search(r'[\s\n\t]', val):
                if candidate == el:
                    return "[%s='%s']" % (attr, val), "//*[@%s='%s']" % (attr, val)
                else:
                    tag = candidate.name
                    return "%s[%s='%s']" % (tag, attr, val), "//%s[@%s='%s']" % (tag, attr, val)
        candidate = candidate.parent
    return None, None


def build_semantic_from_element(anchor_el, target_el, soup):
    """Build (css_selector, xpath) from anchor to target using classes."""
    if not anchor_el or not target_el:
        return None, None

    # Path from target up to anchor
    path_els = []
    el = target_el
    while el and el != anchor_el:
        path_els.insert(0, el)
        el = el.parent

    if not path_els:
        return None, None

    anchor_id = anchor_el.get('id')
    if anchor_id:
        css_anchor = '%s#%s' % (anchor_el.name, anchor_id)
        xpath_anchor = "//%s[@id='%s']" % (anchor_el.name, anchor_id)
    else:
        return None, None

    css_parts = []
    xpath_parts = []
    for part_el in path_els:
        tag = part_el.name
        classes = part_el.get('class', [])
        # Filter useful classes (not utility-only)
        good_classes = [c for c in classes if not re.match(
            r'^(w-|h-|p-|m-|text-|flex|grid|block|inline|hidden|relative|absolute|z-|bg-|border-|rounded|gap-|font-|leading-|tracking-|items-|justify-|cursor-)',
            c
        )]
        if good_classes:
            cls = good_classes[0]
            siblings_same = part_el.find_previous_siblings(tag)
            nth = len(siblings_same) + 1
            if tag in ('li', 'td', 'tr'):
                if nth == 1:
                    css_parts.append('%s:first-child' % tag)
                    xpath_parts.append('%s[1]' % tag)
                else:
                    css_parts.append('%s:nth-child(%d)' % (tag, nth))
                    xpath_parts.append('%s[%d]' % (tag, nth))
            else:
                css_parts.append('.%s' % cls)
                xpath_parts.append("*[contains(@class,'%s')]" % cls)
        elif tag in ('ul', 'ol', 'dl', 'table', 'thead', 'tbody'):
            css_parts.append(tag)
            xpath_parts.append(tag)
        elif tag in ('li', 'td', 'tr'):
            siblings_same = part_el.find_previous_siblings(tag)
            nth = len(siblings_same) + 1
            if nth == 1:
                css_parts.append('%s:first-child' % tag)
                xpath_parts.append('%s[1]' % tag)
            else:
                css_parts.append('%s:nth-child(%d)' % (tag, nth))
                xpath_parts.append('%s[%d]' % (tag, nth))
        elif part_el.get('id'):
            css_parts.append('#' + part_el['id'])
            xpath_parts.append("*[@id='%s']" % part_el['id'])
        else:
            css_parts.append(tag)
            xpath_parts.append(tag)

    css_sel = css_anchor + ' ' + ' '.join(css_parts)
    xpath_sel = xpath_anchor + '//' + '/'.join(xpath_parts)

    return css_sel, xpath_sel


def find_best_anchor(target_el):
    """Walk up from target_el, find best unique anchor (ID, snapshot-N, article, etc.)"""
    el = target_el.parent
    while el and el.name and el.name != '[document]':
        el_id = el.get('id', '')
        # Snapshot containers
        if el_id and re.match(r'snapshot-\d+', el_id):
            return el
        # Named containers with IDs
        if el_id and el_id not in ('__next', 'app', 'root', 'main', 'content',
                                    'any-content', 'adSearchWrapper'):
            return el
        # Article/section with result-like IDs
        if el.name in ('article', 'section') and el_id:
            return el
        el = el.parent
    # Fallback: first named ID found going up
    el = target_el.parent
    while el and el.name and el.name != '[document]':
        if el.get('id'):
            return el
        el = el.parent
    return None


# ─── Main processing ──────────────────────────────────────────────────────────

files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    soup = None
    changes = 0

    for rec in data.get('records', []):
        prov = rec.get('provenance', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue

            css = pv.get('css_selector', '') or ''
            css_abs = pv.get('css_selector_absolute', '') or ''
            xpath = pv.get('xpath', '') or ''
            xpath_abs = pv.get('xpath_absolute', '') or ''

            # Check if css_selector needs fixing
            css_needs_fix = 'nth-of-type' in css and 'first-child' not in css
            # Check if xpath needs fixing (starts with /html/body absolute path)
            xpath_needs_fix = bool(re.search(r'/(html|body)\[', xpath))

            if not css_needs_fix and not xpath_needs_fix:
                continue

            # ── Phase 1: Special known patterns ──────────────────────────────
            # listing_url on detail/listing pages -> link[rel='canonical']
            if field_name == 'listing_url' and pv.get('attribute') == 'href':
                if soup is None and os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                if soup:
                    canonical = soup.find('link', rel='canonical')
                    if canonical:
                        pv['css_selector'] = "link[rel='canonical']"
                        pv['css_selector_absolute'] = get_css_abs(canonical) or css_abs
                        pv['xpath'] = "//link[@rel='canonical']"
                        pv['xpath_absolute'] = get_xpath_abs(canonical) or xpath_abs
                        pv['attribute'] = 'href'
                        changes += 1
                        continue

            # images_urls from meta og:image
            if field_name in ('images_urls', 'primary_image_url') and 'meta' in css:
                if soup is None and os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                if soup:
                    og_meta = soup.find('meta', property='og:image')
                    if og_meta:
                        pv['css_selector'] = "meta[property='og:image']"
                        pv['css_selector_absolute'] = get_css_abs(og_meta) or css_abs
                        pv['xpath'] = "//meta[@property='og:image']"
                        pv['xpath_absolute'] = get_xpath_abs(og_meta) or xpath_abs
                        pv['attribute'] = 'content'
                        changes += 1
                        continue

            # ── Phase 2: Use element's data-* attrs if available ───────────
            if soup is None and os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            if not soup:
                continue

            # Find element via css_selector_absolute
            target_el = None
            if css_abs:
                try:
                    els = soup.select(css_abs)
                    if len(els) == 1:
                        target_el = els[0]
                except Exception:
                    pass

            if not target_el and css_abs:
                # Try xpath_absolute via simple ancestor
                pass

            if not target_el:
                continue

            # Try stable data-* attributes on element or ancestors
            stable_css, stable_xpath = find_stable_attr_selector(target_el)
            if stable_css and stable_xpath:
                n = count_matches(soup, stable_css)
                if n == 1:
                    pv['css_selector'] = stable_css
                    pv['xpath'] = stable_xpath
                    changes += 1
                    continue

            # ── Phase 3: Build semantic from anchor ───────────────────────
            anchor_el = find_best_anchor(target_el)
            if anchor_el:
                new_css, new_xpath = build_semantic_from_element(anchor_el, target_el, soup)
                if new_css:
                    n = count_matches(soup, new_css)
                    if n == 1:
                        pv['css_selector'] = new_css
                        if new_xpath:
                            pv['xpath'] = new_xpath
                        changes += 1
                        continue

            # ── Phase 4: Fix xpath that is still absolute ─────────────────
            if xpath_needs_fix and not css_needs_fix:
                # css_selector is OK, just fix xpath to be semantic (mirror css)
                if css and 'nth-of-type' not in css:
                    # Convert css to xpath approximation
                    inner = css
                    # Simple mirror: replace class selectors
                    inner = re.sub(r'\.([\w-]+)', r"[contains(@class,'\1')]", inner)
                    inner = re.sub(r'#([\w-]+)', r"[@id='\1']", inner)
                    inner = re.sub(r'\[contains\(@class,', '*[contains(@class,', inner)
                    pv['xpath'] = '//' + inner if not inner.startswith('//') else inner
                    changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

print('\nDone.')
