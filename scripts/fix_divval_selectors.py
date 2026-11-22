"""Fix remaining div.val selectors using parent li semantic class."""

import json, re
from bs4 import BeautifulSoup

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

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_APARTMENTS_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_001_LISTING.json'

with open(html_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

changes = 0
for rec_idx, rec in enumerate(data['records']):
    prov = rec.get('provenance', {})
    for field_name, pv in prov.items():
        if not isinstance(pv, dict): continue
        if pv.get('css_selector') != 'div.val': continue

        tq = re.sub(r'\s+', ' ', pv.get('text_quote') or '').strip()
        all_vals = soup.find_all('div', class_='val')
        target = None
        for el in all_vals:
            el_text = re.sub(r'\s+', ' ', el.get_text()).strip()
            if tq and tq in el_text:
                target = el
                break
        if not target:
            continue

        parent_li = target.find_parent('li')
        if not parent_li or not parent_li.get('class'):
            continue

        li_class = parent_li['class'][0]
        has_special = bool(re.search(r'[^a-zA-Z0-9_-]', li_class))

        if has_special:
            # Use attribute word-match selector (avoids CSS special char issue)
            css_new = 'li[class~="%s"] > div.val' % li_class
        else:
            css_new = 'li.%s > div.val' % li_class

        xpath_new = '//li[contains(@class,"%s")]/div[contains(@class,"val")]' % li_class

        pv['css_selector'] = css_new
        pv['xpath'] = xpath_new
        pv['css_selector_absolute'] = get_css_abs(target)
        pv['xpath_absolute'] = get_xpath_abs(target)
        changes += 1

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Fixed %d div.val entries' % changes)

# Verify
with open(json_path, 'r', encoding='utf-8') as f:
    d2 = json.load(f)
for k in ['floor_area', 'Car_Garage']:
    if k in d2['records'][0]['provenance']:
        print(k, '->', d2['records'][0]['provenance'][k]['css_selector'])
