import json
from bs4 import BeautifulSoup
html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
for s in soup.find_all('script'):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data = json.loads(s.string)
        for qv in data.get('queries', {}).values():
            try:
                q_data = json.loads(qv)
                first = q_data.get('data', [])[0]
                attr = first.get('attributes', {})
                print('sub-type:', attr.get('listing-sub-type'))
                print('category-code:', attr.get('listing-category-code'))
                print('listing-type:', attr.get('listing-type'))
                
                print('floor-area:', attr.get('floor-area'))
                print('land-area:', attr.get('land-area'))
                break
            except Exception:
                pass
        break
