import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# The CSS selector suggests it's finding div.line-clamp-1.break-all as the target element
# Find all elements that have only text matching a short name (agent)
for el in soup.find_all('div', class_='line-clamp-1'):
    txt = el.get_text(strip=True)
    if len(txt) > 0 and len(txt) < 30:
        p = el.parent
        if p:
            print(f"text={repr(txt)} | parent class={p.get('class')}")
