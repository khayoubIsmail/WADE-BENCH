import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

scripts = soup.find_all('script')
data_str = None
for s in scripts:
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data_str = s.string
        break

data = json.loads(data_str)
queries = data.get('queries', {})
for qk, qv in queries.items():
    if 'page[limit]=20' in qk:
        q_data = json.loads(qv)
        first = q_data.get('data', [])[0]
        photos = first.get('attributes', {}).get('photos', [])
        print('Photos:', json.dumps(photos[:1], indent=2))
        
        # Check an agent with pic and office with logo
        included = {i['id']: i for i in q_data.get('included', [])}
        for obj in included.values():
            if obj['type'] == 'agent' and obj.get('attributes', {}).get('photo-url'):
                print('Agent photo:', obj['attributes']['photo-url'])
            if obj['type'] == 'office' and obj.get('attributes', {}).get('logo-url'):
                print('Office logo:', obj['attributes']['logo-url'])
        break
