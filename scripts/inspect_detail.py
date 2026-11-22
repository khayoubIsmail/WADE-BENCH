import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

state_script = soup.find('script', id='shoebox-ember-data-storefront')
if state_script and state_script.string:
    data = json.loads(state_script.string)
    print("Found shoebox script. Keys:", data.keys())
    # Let's see what's in data
    # The listing data might be in records or queries
    if 'data' in data:
        print("data keys:", data['data'].keys())
    
    # Dump a summary of the listing object
    # It might be in the data -> first object
    for k, v in data.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, dict) and v2.get('type') == 'listing':
                    print("Found listing:", k2)
                    print(json.dumps(v2, indent=2)[:500])
                    break
else:
    # Maybe a different script?
    print("No shoebox script found. Looking for Next.js or other state...")
    for s in soup.find_all('script'):
        if s.string and 'listing' in s.string.lower() and '{' in s.string:
            print("Found potential script with length:", len(s.string))
            print(s.string[:500])
