import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def print_feature(text):
    el = soup.find('title', string=re.compile(text, re.IGNORECASE))
    if el:
        svg = el.parent
        svg_parent = svg.parent
        print(f"\n--- {text} ---")
        # Go up two levels and print the whole HTML of the block
        block = svg_parent.parent
        if block:
            print(str(block)[:500].encode('ascii', 'ignore').decode())

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
            print("History row:", str(p)[:500].encode('ascii', 'ignore').decode())

