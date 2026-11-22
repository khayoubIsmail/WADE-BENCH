import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

script_content = ""
for s in soup.find_all('script'):
    if s.string and '__reactServerState' in s.string:
        script_content = s.string
        break

if script_content:
    match = re.search(r'root\.__reactServerState\.InitialContext\s*=\s*(\{.*?\});\n', script_content)
    if match:
        json_data = json.loads(match.group(1))
        # Look in "ReactServerAgent.cache"
        cache = json_data.get('ReactServerAgent.cache', {}).get('dataCache', {})
        print(f"Found {len(cache)} items in cache.")
        for k, v in cache.items():
            if 'res' in v and isinstance(v['res'], dict):
                res = v['res']
                if 'numBeds' in str(res):
                    print("Found listing info in:", k)
                    with open('debug_redfin_state.json', 'w') as f:
                        json.dump(res, f, indent=2)
                    break
