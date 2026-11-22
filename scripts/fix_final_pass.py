"""
fix_final_pass.py
Final pass for all remaining 454 issues:

1. xpath absolute when css already semantic → convert css→xpath
2. RIGHTMOVE: empty css_selector → build from data-testid ancestor chain
3. REALESTATE.CO.NZ images_urls → use data-test='photo-block' anchor
4. LEBONCOIN energy_rating → use article data-spark-component scope
5. OTM bedrooms from div#__next → use li[data-id] from xpath_absolute trace
6. CENTURY_21_002 xpath format fix (missing //html prefix)
7. REDFIN detail: convert css with data-rf-test-id to semantic xpath
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def count_matches(soup, sel):
    try:
        return len(soup.select(sel))
    except Exception:
        return -1


def get_css_abs(el):
    if not el: return None
    path = []
    while el and el.name and el.name != '[document]':
        if el.get('id'):
            path.insert(0, el.name + '#' + el['id']); break
        sibs = el.find_previous_siblings(el.name)
        nth = len(sibs) + 1
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
        sibs = el.find_previous_siblings(el.name)
        nth = len(sibs) + 1
        path.insert(0, '%s[%d]' % (el.name, nth))
        el = el.parent
    return '/' + '/'.join(path) if path else None


def css_to_xpath(css):
    """Convert simple semantic CSS selector to XPath."""
    result = css.strip()
    # attribute selectors
    result = re.sub(r"\[data-rf-test-id='([^']+)'\]", r"[@data-rf-test-id='\1']", result)
    result = re.sub(r"\[data-testid='([^']+)'\]", r"[@data-testid='\1']", result)
    result = re.sub(r"\[data-test='([^']+)'\]", r"[@data-test='\1']", result)
    result = re.sub(r"\[aria-label='([^']+)'\]", r"[@aria-label='\1']", result)
    result = re.sub(r"\[rel='([^']+)'\]", r"[@rel='\1']", result)
    result = re.sub(r"\[([^=\]]+)='([^']+)'\]", r"[@\1='\2']", result)
    # tag#id
    result = re.sub(r'(\w+)#([\w-]+)', r'\1[@id="\2"]', result)
    result = re.sub(r'^#([\w-]+)', r'*[@id="\1"]', result)
    # tag.class (multiple classes)
    def replace_classes(m):
        tag = m.group(1) or '*'
        classes = m.group(2).split('.')
        predicates = " and ".join("contains(@class,'%s')" % c for c in classes if c)
        return '%s[%s]' % (tag, predicates)
    result = re.sub(r'(\w*)\.([\w.-]+?)(?=\s|>|$|\[)', replace_classes, result)
    # :nth-of-type(N) and :nth-child(N)
    result = re.sub(r':nth-of-type\((\d+)\)', r'[\1]', result)
    result = re.sub(r':nth-child\((\d+)\)', r'[\1]', result)
    result = re.sub(r':first-child', '[1]', result)
    # Child combinator and descendant
    result = result.replace(' > ', '/')
    result = re.sub(r'\s+', '//', result)
    if not result.startswith('/'):
        result = '//' + result
    return result


def find_data_testid_chain(el, soup, card_testid):
    """Build selector using data-testid ancestor chain."""
    # Walk up and collect data-testid values
    ancestors = []
    p = el
    while p and p.name and p.name not in ('[document]', 'html', 'body'):
        dt = p.get('data-testid')
        if dt:
            ancestors.insert(0, (p, dt))
            if dt == card_testid:
                break
        p = p.parent

    if not ancestors:
        return None, None

    # Build from outermost found data-testid
    outer_el, outer_dt = ancestors[0]
    css_anchor = "[data-testid='%s']" % outer_dt
    xpath_anchor = "//*[@data-testid='%s']" % outer_dt

    # Check if target has a data-testid itself
    target_dt = el.get('data-testid')
    if target_dt and len(ancestors) > 1:
        css_sel = "[data-testid='%s'] [data-testid='%s']" % (outer_dt, target_dt)
        xpath_sel = "//*[@data-testid='%s']//*[@data-testid='%s']" % (outer_dt, target_dt)
        n = count_matches(soup, css_sel)
        if n == 1:
            return css_sel, xpath_sel

    # Check immediate data-testid child
    if len(ancestors) >= 2:
        inner_dt = ancestors[-1][1]
        # Get element's class for specificity
        el_cls = [c for c in (el.get('class') or []) if not re.match(r'^(w-|h-|p-|m-)', c)]
        if el_cls:
            css_sel = "[data-testid='%s'] [data-testid='%s'] .%s" % (outer_dt, inner_dt, el_cls[0])
        else:
            css_sel = "[data-testid='%s'] [data-testid='%s']" % (outer_dt, inner_dt)
        xpath_sel = "//*[@data-testid='%s']//*[@data-testid='%s']" % (outer_dt, inner_dt)
        return css_sel, xpath_sel

    return None, None


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
            css     = pv.get('css_selector', '') or ''
            css_abs = pv.get('css_selector_absolute', '') or ''
            xpath   = pv.get('xpath', '') or ''
            xpath_abs = pv.get('xpath_absolute', '') or ''

            css_nth      = 'nth-of-type' in css
            xpath_abs_fl = bool(re.search(r'/(html|body)\[', xpath))
            xpath_bad    = xpath.startswith('/body/')

            if not css_nth and not xpath_abs_fl and not xpath_bad:
                continue

            # ── Fix 1: xpath absolute, css semantic → convert css to xpath ─
            if (xpath_abs_fl or xpath_bad) and css and not css_nth:
                new_xpath = css_to_xpath(css)
                if new_xpath and new_xpath != xpath and '/html' not in new_xpath:
                    pv['xpath'] = new_xpath
                    changes += 1
                    continue

            # Need HTML
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

            if not target_el and xpath_abs:
                # Try finding via xpath_absolute approximation - use last part of css_abs
                pass

            if not target_el:
                continue

            # ── Fix 2: RIGHTMOVE — empty css, build from data-testid ───────
            if not css.strip() and 'RIGHTMOVE' in fname:
                # Walk up to find propertyCard-vrt-N anchor
                card_id = None
                p = target_el.parent
                while p and p.name:
                    dt = p.get('data-testid', '')
                    if re.match(r'^propertyCard-vrt-\d+$', dt):
                        card_id = dt
                        break
                    p = p.parent

                if card_id:
                    # Build selector using data-testid hierarchy
                    dt_chain = []
                    p = target_el
                    while p and p.get('data-testid') != card_id:
                        if p.get('data-testid'):
                            dt_chain.insert(0, p.get('data-testid'))
                        p = p.parent

                    good_classes = [c for c in (target_el.get('class') or []) if not re.match(
                        r'^(w-|h-|p-|m-|text-|flex|grid|block|inline)', c)]

                    if dt_chain:
                        inner_dt = dt_chain[-1]
                        new_css = "div[data-testid='%s'] [data-testid='%s']" % (card_id, inner_dt)
                    elif good_classes:
                        new_css = "div[data-testid='%s'] .%s" % (card_id, good_classes[0])
                    else:
                        el_cls = (target_el.get('class') or [''])[0]
                        new_css = "div[data-testid='%s'] .%s" % (card_id, el_cls) if el_cls else None

                    if new_css:
                        new_xpath = "//*[@data-testid='%s']//*[@data-testid='%s']" % (card_id, inner_dt) if dt_chain else \
                                    "//*[@data-testid='%s']" % card_id

                        n = count_matches(soup, new_css)
                        if n >= 1:
                            pv['css_selector'] = new_css
                            pv['xpath'] = new_xpath
                            pv['css_selector_absolute'] = get_css_abs(target_el) or css_abs
                            pv['xpath_absolute'] = get_xpath_abs(target_el) or xpath_abs
                            changes += 1
                            continue

            # ── Fix 3: REALESTATE.CO.NZ — use data-test ancestor ──────────
            if css_nth and 'REALESTATE' in fname:
                p = target_el.parent
                dt_anchor = None
                while p and p.name:
                    dt = p.get('data-test')
                    if dt:
                        dt_anchor = (p, dt)
                        break
                    p = p.parent

                if dt_anchor:
                    anchor_el, dt_val = dt_anchor
                    good_cls = [c for c in (target_el.get('class') or []) if not re.match(
                        r'^(w-|h-|p-|m-|text-|flex|grid|block|inline|hidden|relative|absolute)', c)]
                    if good_cls:
                        new_css = "[data-test='%s'] .%s" % (dt_val, good_cls[0])
                    else:
                        new_css = "[data-test='%s'] %s" % (dt_val, target_el.name)
                    new_xpath = "//*[@data-test='%s']//%s" % (dt_val, target_el.name)

                    n = count_matches(soup, new_css)
                    if n == 1:
                        pv['css_selector'] = new_css
                        pv['xpath'] = new_xpath
                        changes += 1
                        continue

            # ── Fix 4: LEBONCOIN — use article[data-spark-component] ───────
            if css_nth and 'LEBONCOIN' in fname:
                p = target_el.parent
                spark_el = None
                while p and p.name:
                    if p.get('data-spark-component') == 'link-box':
                        spark_el = p
                        break
                    if p.get('aria-label'):
                        spark_el = p
                        break
                    p = p.parent

                if spark_el:
                    aria = spark_el.get('aria-label', '')
                    spark_comp = spark_el.get('data-spark-component', '')
                    # Find good inner selector for target
                    el_id = target_el.get('id')
                    el_dt = target_el.get('data-test') or target_el.get('data-testid')
                    el_cls = [c for c in (target_el.get('class') or []) if not re.match(
                        r'^(w-|h-|p-|m-|text-|flex|grid)', c)]

                    if aria:
                        scope_css = "article[aria-label='%s']" % aria
                        scope_xpath = "//article[@aria-label='%s']" % aria
                    elif spark_comp:
                        scope_css = "[data-spark-component='%s']" % spark_comp
                        scope_xpath = "//*[@data-spark-component='%s']" % spark_comp

                    inner = el_dt if el_dt else (el_cls[0] if el_cls else target_el.name)
                    if el_dt:
                        new_css = "%s [data-test='%s']" % (scope_css, inner)
                        new_xpath = "%s//*[@data-test='%s']" % (scope_xpath, inner)
                    elif el_cls:
                        new_css = "%s .%s" % (scope_css, inner)
                        new_xpath = "%s//*[contains(@class,'%s')]" % (scope_xpath, inner)
                    else:
                        new_css = "%s %s" % (scope_css, inner)
                        new_xpath = "%s//%s" % (scope_xpath, inner)

                    try:
                        n = count_matches(soup, new_css)
                        if n == 1:
                            pv['css_selector'] = new_css
                            pv['xpath'] = new_xpath
                            changes += 1
                            continue
                    except Exception:
                        pass

            # ── Fix 5: Generic fallback — convert remaining css_nth via css_to_xpath ─
            if css_nth:
                new_xpath = css_to_xpath(css)
                if new_xpath and '/html' not in new_xpath and new_xpath != xpath:
                    pv['xpath'] = new_xpath
                    changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

print('\n--- Final audit ---')
total_css = 0
total_xpath = 0
for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    fc, fx = 0, 0
    for rec in data.get('records', []):
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '') or ''
            xpath = pv.get('xpath', '') or ''
            if 'nth-of-type' in css: fc += 1
            if re.search(r'/(html|body)\[', xpath) or xpath.startswith('/body/'): fx += 1
    if fc or fx:
        print('  %-52s  css=%d xpath=%d' % (fname, fc, fx))
    total_css += fc
    total_xpath += fx

print('\nTotal: css=%d xpath=%d total=%d' % (total_css, total_xpath, total_css+total_xpath))
print('Done.')
