"""
fix_semantic_site_aware.py
Site-aware semantic selector restoration for all remaining nth-of-type/xpath-absolute issues.

Known card anchors per site:
  DAFT.IE         -> li[data-testid='result-XXXXXX']
  ONTHEMARKET     -> li[data-id='XXXXXX']
  RIGHTMOVE       -> div[data-testid='propertyCard-vrt-N']
  LEBONCOIN       -> article[aria-label='...']
  FINN_EIENDOM    -> h2#search-ad-XXXXXX (walk to article ancestor)

Also fixes:
  - Empty css_selector when css_selector_absolute exists
  - xpath = //html/body[1]/... absolute paths -> semantic form mirroring css_selector
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'

# ─── Anchor detection ─────────────────────────────────────────────────────────

ANCHOR_PATTERNS = [
    # (css_attr, css_attr_prefix, result_css_fmt, result_xpath_fmt)
    ('data-testid', r'^result-', "li[data-testid='{val}']", "//li[@data-testid='{val}']"),
    ('data-id',     r'^\d+$',   "li[data-id='{val}']",     "//li[@data-id='{val}']"),
    ('data-testid', r'^propertyCard-vrt-', "div[data-testid='{val}']", "//div[@data-testid='{val}']"),
    ('aria-label',  None,        "article[aria-label='{val}']", "//article[@aria-label='{val}']"),
]


def find_card_anchor(el):
    """Walk up from el to find the listing-card anchor. Returns (anchor_el, css_anchor, xpath_anchor)."""
    p = el.parent
    for _ in range(15):
        if not p or not p.name or p.name in ('[document]', 'html', 'body'):
            break
        for attr, val_pattern, css_fmt, xpath_fmt in ANCHOR_PATTERNS:
            val = p.get(attr)
            if val:
                val_str = val if not isinstance(val, list) else ' '.join(val)
                if val_pattern is None or re.search(val_pattern, val_str):
                    css_anchor = css_fmt.format(val=val_str.replace("'", "\\'"))
                    xpath_anchor = xpath_fmt.format(val=val_str.replace("'", "\\'"))
                    return p, css_anchor, xpath_anchor
        # Also check h2[id^='search-ad-']
        if p.name == 'h2' and re.match(r'^search-ad-', p.get('id', '')):
            h2_id = p['id']
            # Walk up to find article
            article = p.parent
            while article and article.name != 'article':
                article = article.parent
            if article:
                css_anchor = "article:has(h2#%s)" % h2_id
                xpath_anchor = "//article[.//h2[@id='%s']]" % h2_id
                return article, css_anchor, xpath_anchor
            else:
                css_anchor = "h2#%s" % h2_id
                xpath_anchor = "//h2[@id='%s']" % h2_id
                return p, css_anchor, xpath_anchor
        # Generic ID fallback (not too broad)
        el_id = p.get('id', '')
        if el_id and el_id not in ('__next', 'app', 'root', 'main', 'content',
                                    'any-content', 'adSearchWrapper', 'l-searchResults',
                                    'skip-to-results'):
            css_anchor = "%s#%s" % (p.name, el_id)
            xpath_anchor = "//%s[@id='%s']" % (p.name, el_id)
            return p, css_anchor, xpath_anchor
        p = p.parent
    return None, None, None


def build_inner_path(anchor_el, target_el):
    """Build CSS and XPath inner path from anchor_el to target_el using classes."""
    path_els = []
    el = target_el
    while el and el != anchor_el:
        path_els.insert(0, el)
        el = el.parent
        if not el:
            break

    if not path_els:
        return '', ''

    css_parts = []
    xpath_parts = []

    for part_el in path_els:
        tag = part_el.name
        classes = part_el.get('class', [])
        el_id = part_el.get('id')
        data_test = part_el.get('data-test') or part_el.get('data-testid') or part_el.get('data-tracking')

        # Priority: data-test > ID > meaningful class > positional
        if data_test:
            css_parts.append("[data-test='%s']" % data_test if part_el.get('data-test')
                              else "[data-testid='%s']" % data_test if part_el.get('data-testid')
                              else "[data-tracking='%s']" % data_test)
            xpath_parts.append("*[@data-test='%s' or @data-testid='%s']" % (data_test, data_test))
        elif el_id:
            css_parts.append('#%s' % el_id)
            xpath_parts.append("*[@id='%s']" % el_id)
        elif classes:
            # Filter utility/generated classes
            good = [c for c in classes if not re.match(
                r'^(w-|h-|p-|m-|text-|flex|grid|block|inline|hidden|relative|absolute|z-|bg-|border-|rounded|gap-|font-|leading-|tracking-|items-|justify-|cursor-|overflow-|transition-|duration-|ease-|opacity-|pointer-|select-|shadow-|ring-|inset-|space-|translate-|rotate-|scale-|transform|group|peer|sr-only|sc-)',
                c
            )]
            if good:
                cls = good[0]
                siblings = part_el.find_previous_siblings(tag)
                nth = len(siblings) + 1
                if tag in ('li', 'td', 'tr', 'dt', 'dd'):
                    if nth == 1:
                        css_parts.append('%s:first-child' % tag)
                        xpath_parts.append('%s[1]' % tag)
                    else:
                        css_parts.append('%s:nth-child(%d)' % (tag, nth))
                        xpath_parts.append('%s[%d]' % (tag, nth))
                else:
                    css_parts.append('.%s' % cls)
                    xpath_parts.append("*[contains(@class,'%s')]" % cls)
            else:
                # All utility classes — use positional
                siblings = part_el.find_previous_siblings(tag)
                nth = len(siblings) + 1
                if tag in ('li', 'td', 'tr', 'dt', 'dd'):
                    if nth == 1:
                        css_parts.append('%s:first-child' % tag)
                        xpath_parts.append('%s[1]' % tag)
                    else:
                        css_parts.append('%s:nth-child(%d)' % (tag, nth))
                        xpath_parts.append('%s[%d]' % (tag, nth))
                else:
                    css_parts.append(tag)
                    xpath_parts.append(tag)
        elif tag in ('ul', 'ol', 'dl', 'table', 'address', 'header', 'footer', 'nav', 'main', 'aside'):
            css_parts.append(tag)
            xpath_parts.append(tag)
        elif tag in ('li', 'td', 'tr', 'dt', 'dd'):
            siblings = part_el.find_previous_siblings(tag)
            nth = len(siblings) + 1
            if nth == 1:
                css_parts.append('%s:first-child' % tag)
                xpath_parts.append('%s[1]' % tag)
            else:
                css_parts.append('%s:nth-child(%d)' % (tag, nth))
                xpath_parts.append('%s[%d]' % (tag, nth))
        else:
            css_parts.append(tag)
            xpath_parts.append(tag)

    return ' '.join(css_parts), '/'.join(xpath_parts)


def count_matches(soup, sel):
    try:
        return len(soup.select(sel))
    except Exception:
        return -1


def css_to_xpath_approx(css):
    """Very rough CSS -> XPath approximation for simple selectors."""
    if not css:
        return ''
    result = css
    # Replace ID selectors
    result = re.sub(r'(\w+)#([\w-]+)', r'\1[@id="\2"]', result)
    result = re.sub(r'^#([\w-]+)', r'*[@id="\1"]', result)
    # Replace class selectors
    result = re.sub(r'\.([^.\s>~+\[]+)', r'[contains(@class,"\1")]', result)
    # Replace attribute selectors
    result = re.sub(r'\[([^\]]+)=\'([^\']+)\'\]', r'[@\1="\2"]', result)
    # Replace child combinator
    result = result.replace(' > ', '/')
    # Replace space (descendant)
    result = re.sub(r'\s+', '//', result)
    return '//' + result.lstrip('/')


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

            css     = pv.get('css_selector', '') or ''
            css_abs = pv.get('css_selector_absolute', '') or ''
            xpath   = pv.get('xpath', '') or ''
            xpath_abs = pv.get('xpath_absolute', '') or ''

            # Conditions to fix:
            css_has_nth    = 'nth-of-type' in css
            css_is_empty   = not css.strip()
            xpath_absolute = bool(re.search(r'/(html|body)\[', xpath))

            if not css_has_nth and not css_is_empty and not xpath_absolute:
                continue

            # Load HTML lazily
            if soup is None and os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            if not soup:
                continue

            # Find target element via css_selector_absolute
            target_el = None
            if css_abs:
                try:
                    els = soup.select(css_abs)
                    if len(els) == 1:
                        target_el = els[0]
                except Exception:
                    pass

            if target_el is None:
                # Fall back to xpath_absolute -> find via positional XPath approx
                if css_is_empty and css_abs:
                    pass  # can't find element, skip
                continue

            # Find card anchor
            anchor_el, css_anchor, xpath_anchor = find_card_anchor(target_el)

            if anchor_el:
                inner_css, inner_xpath = build_inner_path(anchor_el, target_el)

                if inner_css:
                    new_css = '%s %s' % (css_anchor, inner_css)
                    new_xpath = '%s//%s' % (xpath_anchor, inner_xpath)

                    n = count_matches(soup, new_css)
                    if n == 1:
                        if css_has_nth or css_is_empty:
                            pv['css_selector'] = new_css
                            changes += 1
                        if xpath_absolute or not xpath.strip():
                            pv['xpath'] = new_xpath
                            changes += 1
                        continue
                    # If not unique, try with full inner absolute path (nth-of-type kept for inner)
                    # Fallback: use anchor + absolute inner
                    if css_has_nth and anchor_el:
                        # At least replace the outer absolute path with anchor
                        try:
                            anchor_sel = '%s' % css_anchor
                            # Find anchor position in css_abs
                            new_css2 = anchor_sel + ' ' + inner_css
                            n2 = count_matches(soup, new_css2)
                            if n2 >= 1:
                                pv['css_selector'] = new_css2
                                pv['xpath'] = new_xpath
                                changes += 1
                                continue
                        except Exception:
                            pass

            # ── Fix xpath-only when css is already semantic ────────────────
            if xpath_absolute and not css_is_empty and not css_has_nth:
                new_xpath = css_to_xpath_approx(css)
                if new_xpath and new_xpath != xpath:
                    pv['xpath'] = new_xpath
                    changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

print('\n--- Post-fix audit ---')
total = 0
for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    issues = 0
    for rec in data.get('records', []):
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '') or ''
            xpath = pv.get('xpath', '') or ''
            if 'nth-of-type' in css:
                issues += 1
            if re.search(r'/(html|body)\[', xpath):
                issues += 1
    if issues:
        print('  %-55s  %d remaining' % (fname, issues))
    total += issues

print('\nTotal remaining issues: %d' % total)
print('Done.')
