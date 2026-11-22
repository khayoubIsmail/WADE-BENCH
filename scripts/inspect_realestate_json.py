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

if data_str:
    data = json.loads(data_str)
    queries = data.get('queries', {})
    for qk, qv in queries.items():
        if 'page[limit]=20' in qk:
            try:
                q_data = json.loads(qv)
                listings = q_data.get('data', [])
                if listings:
                    print('Found query:', qk)
                    print('Number of listings:', len(listings))
                    first = listings[0]
                    print('Keys of listing:', list(first.keys()))
                    print('Attributes:', list(first.get('attributes', {}).keys()))
                    # Look at relationships
                    print('Relationships:', list(first.get('relationships', {}).keys()))
                    
                    included = q_data.get('included', [])
                    print('Total included records:', len(included))
                    if len(included) > 0:
                        inc_types = set(i.get('type') for i in included)
                        print('Included types:', inc_types)
                        
            except Exception as e:
                print('Error parsing query value', e)
