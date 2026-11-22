import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Check what "515m" really looks like
print("=== Area text check ===")
for el in soup.find_all(['div', 'span']):
    t = el.get_text(strip=True)
    if '515' in t and len(t) < 10:
        print(repr(t), '| tag:', el.name, '| class:', el.get('class'))

# Check bedrooms structure
print()
print("=== Beds 4 context ===")
for el in soup.find_all(['div', 'span', 'strong']):
    t = el.get_text(strip=True)
    if t == '4':
        p = el.parent
        gp = p.parent if p else None
        ggp = gp.parent if gp else None
        p_text = p.get_text(strip=True)[:60] if p else ''
        print(f"  el: <{el.name} class={el.get('class')}> | parent: <{p.name if p else ''} class={p.get('class') if p else ''}> | parent_text: {repr(p_text)}")

# Check agent_branding structure
print()
print("=== Agent branding (office name) ===")
# load the office name from state
for s in soup.find_all('script'):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data = json.loads(s.string)
        for qv in data.get('queries', {}).values():
            try:
                q_data = json.loads(qv)
                included = {i['id']: i for i in q_data.get('included', [])}
                first = q_data.get('data', [])[0]
                offices = first.get('relationships', {}).get('offices', {}).get('data', [])
                for o in offices:
                    off = included.get(o['id'], {}).get('attributes', {})
                    print(f"Office name: {off.get('name')}, colloquial: {off.get('colloquial-name')}")
            except Exception as e:
                print('err:', e)
        break
