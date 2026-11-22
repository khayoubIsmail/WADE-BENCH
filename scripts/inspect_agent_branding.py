import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Load office colloquial names
for s in soup.find_all('script'):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data = json.loads(s.string)
        for qv in data.get('queries', {}).values():
            try:
                q_data = json.loads(qv)
                included = {i['id']: i for i in q_data.get('included', [])}
                for listing in q_data.get('data', []):
                    offices = listing.get('relationships', {}).get('offices', {}).get('data', [])
                    for o in offices[:1]:
                        off = included.get(o['id'], {}).get('attributes', {})
                        cname = off.get('colloquial-name')
                        print(f"Colloquial name: {repr(cname)}")
                        # Search DOM for it
                        for el in soup.find_all(string=lambda t: t and cname and cname in t):
                            if el.parent.name not in ['script', 'style']:
                                print(f"  Found in DOM: <{el.parent.name}> class={el.parent.get('class')} | {el.strip()[:60]}")
                    break
            except Exception as e:
                print('err:', e)
        break
