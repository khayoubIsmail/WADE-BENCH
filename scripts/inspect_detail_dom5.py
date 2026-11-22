import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def get_feature(text):
    el = soup.find('title', string=re.compile(text, re.IGNORECASE))
    if el:
        svg = el.parent
        svg_container = svg.parent
        feature_container = svg_container.parent
        val = feature_container.get_text(strip=True).replace(el.get_text(strip=True), '').strip()
        print(f"{text}: {val}")
        return feature_container

print("--- Properties ---")
get_feature('Bedroom')
get_feature('Bathroom')
get_feature('Floor area')
get_feature('Land area')
get_feature('Garage')

print("\n--- Dates ---")
# For dates, look for 'Sold' in a sale-history-row
for row in soup.find_all('div', attrs={'data-test': 'sale-history-row'}):
    texts = [t.strip() for t in row.stripped_strings if t.strip()]
    if 'Sold' in texts:
        print("Sold history row:", texts)

print("\n--- Price ---")
# Price is probably the first Automated estimate or something similar
dollar = soup.find('div', string=re.compile(r'^\s*dollar\s*$'))
if dollar:
    print("Price next sibling:", dollar.find_next_sibling('h3').get_text(strip=True))

