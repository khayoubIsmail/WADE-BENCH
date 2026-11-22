import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

prices = soup.find_all(string=re.compile(r'\$'))
for p in prices:
    if 'K' in p or ',' in p:
        if p.parent and p.parent.name not in ['script', 'style']:
            print("Price:", repr(p), "Parent:", p.parent.name, p.parent.get('class'))
