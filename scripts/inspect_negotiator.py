import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Find the agent negotiator name element
for s in soup.find_all('script'):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data = json.loads(s.string)
        for qv in data.get('queries', {}).values():
            try:
                q_data = json.loads(qv)
                included = {i['id']: i for i in q_data.get('included', [])}
                first = q_data.get('data', [])[0]
                agents = first.get('relationships', {}).get('agents', {}).get('data', [])
                agent = included.get(agents[0]['id'], {}).get('attributes', {})
                name = f"{agent.get('first-name', '')} {agent.get('last-name', '')}".strip()
                print(f"Looking for agent name: {repr(name)}")
                for el in soup.find_all(['span', 'div', 'p', 'a']):
                    if el.get_text(strip=True) == name:
                        p = el.parent
                        print(f"Found: <{el.name} class={el.get('class')}> | parent: <{p.name} class={p.get('class')}>")
            except Exception as e:
                print('err:', e)
        break
