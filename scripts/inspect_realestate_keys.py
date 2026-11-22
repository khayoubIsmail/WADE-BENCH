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
                if 'included' in q_data:
                    agent = next((i for i in q_data['included'] if i['type'] == 'agent'), None)
                    if agent: print('Agent keys:', agent.get('attributes', {}).keys())
                    office = next((i for i in q_data['included'] if i['type'] == 'office'), None)
                    if office: print('Office keys:', office.get('attributes', {}).keys())
            except Exception:
                pass
        break
