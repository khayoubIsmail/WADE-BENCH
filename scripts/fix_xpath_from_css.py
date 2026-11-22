"""
fix_xpath_from_css.py
Final cleanup:
  1. Convert css_selector -> xpath even when css has nth-of-type (class/ID anchored = still good)
  2. CENTURY_21 open_house_schedule -> use href fragment as unique scope
  3. LEBONCOIN img elements -> use [data-qa-id='aditem_container'] + img[src*='...']
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def css_to_xpath(css):
    """Convert CSS selector to approximate XPath."""
    result = css.strip()
    # data-* attributes
    result = re.sub(r"\[data-rf-test-id='([^']+)'\]", r"[@data-rf-test-id='\1']", result)
    result = re.sub(r"\[data-testid='([^']+)'\]", r"[@data-testid='\1']", result)
    result = re.sub(r"\[data-test='([^']+)'\]", r"[@data-test='\1']", result)
    result = re.sub(r"\[data-spark-component='([^']+)'\]", r"[@data-spark-component='\1']", result)
    result = re.sub(r"\[aria-label='([^']+)'\]", r"[@aria-label='\1']", result)
    result = re.sub(r"\[rel='([^']+)'\]", r"[@rel='\1']", result)
    result = re.sub(r"\[([^=\]'\s]+)='([^']+)'\]", r"[@\1='\2']", result)
    # href contains
    result = re.sub(r"\[href\*='([^']+)'\]", r"[contains(@href,'\1')]", result)
    # tag#id
    result = re.sub(r'(\w+)#([\w-]+)', r'\1[@id="\2"]', result)
    result = re.sub(r'^#([\w-]+)', r'*[@id="\1"]', result)
    # multi-class: tag.cls1.cls2
    def multi_class(m):
        tag = m.group(1) or '*'
        classes = [c for c in m.group(2).split('.') if c]
        preds = " and ".join("contains(@class,'%s')" % c for c in classes)
        return '%s[%s]' % (tag, preds)
    result = re.sub(r'(\w*)\.([\w.-]+?)(?=\s|>|$|\[|:)', multi_class, result)
    # :nth-of-type, :nth-child, :first-child
    result = re.sub(r':nth-of-type\((\d+)\)', r'[\1]', result)
    result = re.sub(r':nth-child\((\d+)\)', r'[\1]', result)
    result = re.sub(r':first-child', '[1]', result)
    # child combinator -> /
    result = result.replace(' > ', '/')
    # descendant -> //
    result = re.sub(r' +', '//', result)
    # prefix
    if not result.startswith('/'):
        result = '//' + result
    return result


def count_matches(soup, sel):
    try:
        return len(soup.select(sel))
    except Exception:
        return -1


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
        fields = rec.get('fields', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue
            css   = pv.get('css_selector', '') or ''
            xpath = pv.get('xpath', '') or ''
            css_abs = pv.get('css_selector_absolute', '') or ''

            xpath_bad = bool(re.search(r'/(html|body)\[', xpath)) or xpath.startswith('/body/')

            # ── Fix 1: Convert css -> xpath regardless of nth-of-type in css ─
            # Only if css is better than full absolute (has class/ID/data-* anchor)
            if xpath_bad and css:
                has_anchor = bool(re.search(r'(#[\w-]+|\[data-|\.[\w-]+)', css))
                if has_anchor:
                    new_xpath = css_to_xpath(css)
                    # Sanity: new xpath shouldn't start with /html
                    if new_xpath and '/html' not in new_xpath and new_xpath != xpath:
                        pv['xpath'] = new_xpath
                        changes += 1
                        continue

            # ── Fix 2: CENTURY_21 open_house_schedule ─────────────────────
            if 'CENTURY_21' in fname and field_name == 'open_house_schedule' and 'nth-of-type' in css:
                if soup is None and os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                if not soup:
                    continue

                # Get the listing URL to extract slug
                url_val = fields.get('listing_url', {}).get('value', '') or \
                          fields.get('listing_url', {}).get('normalized', '')
                if url_val:
                    # Extract unique slug from URL
                    slug = re.search(r'/([^/]+)/lid-', str(url_val))
                    if slug:
                        slug_str = slug.group(1)
                        new_css = "a[href*='/%s/'] span.info-badge" % slug_str
                        n = count_matches(soup, new_css)
                        if n == 1:
                            new_xpath = "//a[contains(@href,'/%s/')]//*[contains(@class,'info-badge')]" % slug_str
                            pv['css_selector'] = new_css
                            pv['xpath'] = new_xpath
                            changes += 1
                            continue

            # ── Fix 3: LEBONCOIN img with empty aria-label ────────────────
            if 'LEBONCOIN' in fname and 'nth-of-type' in css and 'adSearchWrapper' in css:
                if soup is None and os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                if not soup:
                    continue

                # Find element via css_abs
                target_el = None
                if css_abs:
                    try:
                        els = soup.select(css_abs)
                        if len(els) == 1:
                            target_el = els[0]
                    except Exception:
                        pass

                if target_el:
                    # Get listing URL to scope
                    url_val = fields.get('listing_url', {}).get('value', '') or \
                              fields.get('listing_url', {}).get('normalized', '')
                    if url_val:
                        url_id = re.search(r'/(\d+)(?:\.|$|/)', str(url_val))
                        if url_id:
                            uid = url_id.group(1)
                            # Try using a[href*='uid'] scope
                            el_name = target_el.name
                            el_src = target_el.get('src', '')
                            el_cls = [c for c in (target_el.get('class') or []) if c]

                            if el_name == 'img' and el_src:
                                # Use img src fragment
                                src_frag = el_src.split('/')[-1].split('?')[0][:20]
                                if src_frag:
                                    new_css = "a[href*='%s'] img[src*='%s']" % (uid, src_frag)
                                    n = count_matches(soup, new_css)
                                    if n == 1:
                                        new_xpath = "//a[contains(@href,'%s')]//img[contains(@src,'%s')]" % (uid, src_frag)
                                        pv['css_selector'] = new_css
                                        pv['xpath'] = new_xpath
                                        changes += 1
                                        continue
                            elif el_cls:
                                new_css = "a[href*='%s'] .%s" % (uid, el_cls[0])
                                n = count_matches(soup, new_css)
                                if n == 1:
                                    new_xpath = "//a[contains(@href,'%s')]//*[contains(@class,'%s')]" % (uid, el_cls[0])
                                    pv['css_selector'] = new_css
                                    pv['xpath'] = new_xpath
                                    changes += 1
                                    continue

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  fixed=%d' % (fname, changes))

print('\n--- Absolute final audit ---')
total_css, total_xpath = 0, 0
for fname in files:
    with open(os.path.join(GOLD_DIR, fname), 'r', encoding='utf-8') as f:
        data = json.load(f)
    fc, fx = 0, 0
    for rec in data.get('records', []):
        for fn, pv in rec.get('provenance', {}).items():
            if not isinstance(pv, dict): continue
            css = pv.get('css_selector', '') or ''
            xpath = pv.get('xpath', '') or ''
            if 'nth-of-type' in css:
                fc += 1
            if re.search(r'/(html|body)\[', xpath) or xpath.startswith('/body/'):
                fx += 1
    if fc or fx:
        print('  %-52s  css=%d xpath=%d' % (fname, fc, fx))
    total_css += fc; total_xpath += fx

print('\nTotal: css=%d xpath=%d total=%d' % (total_css, total_xpath, total_css+total_xpath))
print('Done.')
