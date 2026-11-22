from bs4 import BeautifulSoup
import os, re, json

SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'
GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'

# CENTURY_21: check href scoping
snap = 'SNAP_REAL_CENTURY_21_001_LISTING'
with open(os.path.join(SNAP_DIR, snap, 'page.html'), 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
with open(os.path.join(GOLD_DIR, 'WBV1_REAL_CENTURY_21_001_LISTING.json'), 'r', encoding='utf-8') as f:
    c21 = json.load(f)

url_val = c21['records'][0]['fields'].get('listing_url', {}).get('value','')
print('C21 listing URL:', url_val[:80])
pid = re.search(r'/pid_(\d+)/', url_val)
if pid:
    pid_num = pid.group(1)
    scope = "a[href*='/pid_%s/'] span.info-badge" % pid_num
    n = len(soup.select(scope))
    print('  href scope matches:', n, '| selector:', scope[:60])

n_global = len(soup.select('.status-badges span.info-badge'))
print('Global .status-badges span.info-badge:', n_global)

# LEBONCOIN: data-qa-id anchor
snap2 = 'SNAP_REAL_LEBONCOIN_001_LISTING'
with open(os.path.join(SNAP_DIR, snap2, 'page.html'), 'r', encoding='utf-8') as f:
    soup2 = BeautifulSoup(f.read(), 'html.parser')
with open(os.path.join(GOLD_DIR, 'WBV1_REAL_LEBONCOIN_001_LISTING.json'), 'r', encoding='utf-8') as f:
    lb = json.load(f)

pv_er = lb['records'][0]['provenance'].get('energy_rating', {})
abs_er = pv_er.get('css_selector_absolute') or pv_er.get('css_selector','')
print()
print('LEBONCOIN energy_rating abs:', abs_er[:80])
try:
    els = soup2.select(abs_er)
    if els:
        el = els[0]
        print('  el:', el.name, 'src=', el.get('src','')[:50])
        p = el.parent
        for i in range(12):
            if not p or not p.name: break
            qa = p.get('data-qa-id','')
            if qa:
                print('  [%d] data-qa-id=%s on %s.%s' % (i, qa, p.name, (p.get('class') or [''])[0]))
                print('  el.parent.cls:', el.parent.get('class'))
                print('  el.pp.cls:', el.parent.parent.get('class') if el.parent.parent else None)
                break
            p = p.parent
except Exception as e:
    print('ERROR:', e)
