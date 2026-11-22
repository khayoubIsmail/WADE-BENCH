"""
fix_remaining_targeted.py
Targeted fixes for specific remaining patterns:
  1. FINN_EIENDOM: use //article[.//h2[@id='search-ad-XX']] as XPath anchor
  2. RIGHTMOVE: convert semantic css_selector -> xpath (images_urls, description)
  3. OTM/LEBONCOIN: fix nth-of-type inside known id anchors (li#result-XX, div#adSearchWrapper)
  4. CENTURY_21: open_house_schedule inside main#any-content
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


def build_class_path(anchor_el, target_el):
    """Build inner CSS and XPath from anchor to target, preferring classes."""
    path_els = []
    el = target_el
    while el and el != anchor_el:
        path_els.insert(0, el)
        el = el.parent
    if not path_els:
        return None, None

    css_parts, xpath_parts = [], []
    for part in path_els:
        tag = part.name
        dt = part.get('data-test') or part.get('data-testid')
        cls = [c for c in (part.get('class') or []) if not re.match(
            r'^(w-|h-|p-|m-|text-|flex|grid|block|inline|hidden|relative|absolute|z-|bg-|border-|rounded|gap-|font-|leading-|tracking-|items-|justify-|cursor-|overflow-|transition-|duration-|ease-|opacity-|pointer-|select-|shadow-|ring-|space-|sr-only|sc-)',
            c
        )]
        pid = part.get('id')
        sibs = part.find_previous_siblings(tag)
        nth = len(sibs) + 1

        if dt:
            css_parts.append("[data-test='%s']" % dt if part.get('data-test') else "[data-testid='%s']" % dt)
            xpath_parts.append("*[@data-test='%s' or @data-testid='%s']" % (dt, dt))
        elif pid:
            css_parts.append('#' + pid)
            xpath_parts.append("*[@id='%s']" % pid)
        elif cls:
            if tag in ('li', 'td', 'tr', 'dt', 'dd'):
                frag = 'li:nth-child(%d)' % nth if nth > 1 else 'li:first-child'
                css_parts.append(frag)
                xpath_parts.append('%s[%d]' % (tag, nth))
            else:
                css_parts.append('.%s' % cls[0])
                xpath_parts.append("*[contains(@class,'%s')]" % cls[0])
        elif tag in ('ul', 'ol', 'dl', 'table', 'address', 'article', 'section', 'nav', 'aside'):
            css_parts.append(tag)
            xpath_parts.append(tag)
        elif tag in ('li', 'td', 'tr', 'dt', 'dd'):
            frag = '%s:nth-child(%d)' % (tag, nth) if nth > 1 else '%s:first-child' % tag
            css_parts.append(frag)
            xpath_parts.append('%s[%d]' % (tag, nth))
        else:
            css_parts.append(tag)
            xpath_parts.append(tag)

    return ' '.join(css_parts), '/'.join(xpath_parts)


def css_to_xpath(css):
    """Rough conversion of semantic CSS to XPath."""
    result = css.strip()
    result = re.sub(r"(\w+)\[data-testid='([^']+)'\]", r"\1[@data-testid='\2']", result)
    result = re.sub(r"\[data-testid='([^']+)'\]", r"*[@data-testid='\1']", result)
    result = re.sub(r"(\w+)\[data-test='([^']+)'\]", r"\1[@data-test='\2']", result)
    result = re.sub(r"\[data-test='([^']+)'\]", r"*[@data-test='\1']", result)
    result = re.sub(r"(\w+)#([\w-]+)", r"\1[@id='\2']", result)
    result = re.sub(r"#([\w-]+)", r"*[@id='\1']", result)
    result = re.sub(r"\.([\w-]+)", r"[contains(@class,'\1')]", result)
    result = re.sub(r"(\w)\[contains", r"\1*[contains", result)
    result = result.replace(' > ', '/')
    result = re.sub(r' +', '//', result)
    if not result.startswith('//'):
        result = '//' + result
    return result


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

            css_nth    = 'nth-of-type' in css
            xpath_abs_flag = bool(re.search(r'/(html|body)\[', xpath))

            if not css_nth and not xpath_abs_flag:
                continue

            if soup is None and os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            if not soup:
                continue

            # ── Fix 1: xpath absolute when css is already semantic ─────────
            if xpath_abs_flag and not css_nth and css:
                new_xpath = css_to_xpath(css)
                if new_xpath and new_xpath != xpath:
                    pv['xpath'] = new_xpath
                    changes += 1
                    continue

            # ── Find target element ────────────────────────────────────────
            target_el = None
            if css_abs:
                try:
                    els = soup.select(css_abs)
                    if len(els) == 1:
                        target_el = els[0]
                except Exception:
                    pass
            if not target_el:
                continue

            # ── Fix 2: FINN_EIENDOM — find article ancestor, use h2 ID ────
            if 'FINN' in fname:
                article_el = None
                p = target_el.parent
                while p and p.name:
                    if p.name == 'article':
                        article_el = p
                        break
                    p = p.parent

                if article_el:
                    h2 = article_el.find('h2', id=re.compile(r'^search-ad-'))
                    if h2:
                        h2_id = h2['id']
                        css_anchor = "article:has(h2#%s)" % h2_id
                        xpath_anchor = "//article[.//h2[@id='%s']]" % h2_id

                        inner_css, inner_xpath = build_class_path(article_el, target_el)
                        if inner_css:
                            new_css = '%s %s' % (css_anchor, inner_css)
                            new_xpath = '%s//%s' % (xpath_anchor, inner_xpath)
                            # Validate uniqueness via article count (not css :has)
                            articles_with_h2 = [a for a in soup.find_all('article')
                                                if a.find('h2', id=h2_id)]
                            if len(articles_with_h2) == 1:
                                pv['css_selector'] = new_css
                                pv['xpath'] = new_xpath
                                changes += 1
                                continue

            # ── Fix 3: selector with nth-of-type inside a unique ID anchor ─
            # e.g. li#result-XX > article > div:nth-of-type(N) > ...
            # Extract the leading ID-based prefix and re-build inner path
            m = re.match(r'^([\w.#\[\]=\'-]+(?:\[[\w\s=\'-]+\])*)\s*(?:>|>)\s*', css)
            if css_nth and css_abs:
                # Walk up to find first named anchor in CSS abs path
                p = target_el.parent
                anchor_el = None
                for _ in range(12):
                    if not p or not p.name: break
                    pid = p.get('id', '')
                    if pid and pid not in ('__next','app','root','main','content',
                                          'any-content','adSearchWrapper','l-searchResults',
                                          'skip-to-results','container'):
                        anchor_el = p
                        break
                    p = p.parent

                if anchor_el:
                    anchor_id = anchor_el['id']
                    css_anchor = '%s#%s' % (anchor_el.name, anchor_id)
                    xpath_anchor = "//%s[@id='%s']" % (anchor_el.name, anchor_id)
                    inner_css, inner_xpath = build_class_path(anchor_el, target_el)
                    if inner_css:
                        new_css = '%s %s' % (css_anchor, inner_css)
                        new_xpath = '%s//%s' % (xpath_anchor, inner_xpath)
                        n = count_matches(soup, new_css)
                        if n == 1:
                            pv['css_selector'] = new_css
                            pv['xpath'] = new_xpath
                            changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

print('\n--- Final audit ---')
total = 0
for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    issues = 0
    for rec in data.get('records', []):
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector','') or ''
            xpath = pv.get('xpath','') or ''
            if 'nth-of-type' in css:
                issues += 1
            if re.search(r'/(html|body)\[', xpath):
                issues += 1
    if issues:
        print('  %-52s  %d remaining' % (fname, issues))
    total += issues

print('\nTotal remaining: %d' % total)
print('Done.')
