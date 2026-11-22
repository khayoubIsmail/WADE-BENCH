import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def print_feature(text):
    el = soup.find('title', string=re.compile(text, re.IGNORECASE))
    if el:
        svg = el.parent
        feature_container = svg.parent
        print(f"--- {text} ---")
        print("Feature value:", feature_container.get_text(strip=True).replace(el.get_text(strip=True), '').strip())

print_feature('Bedroom')
print_feature('Bathroom')
print_feature('Floor area')
print_feature('Land area')
print_feature('Garage')

print("\n--- History Dates ---")
for el in soup.find_all(string=re.compile('Sold', re.IGNORECASE)):
    if el.parent and el.parent.name != 'script':
        p = el.parent.parent.parent
        if p:
            print("History row:", p.get_text(" | ", strip=True))

