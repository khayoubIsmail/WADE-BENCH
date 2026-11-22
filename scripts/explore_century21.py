import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_CENTURY_21_001_LISTING\page.html'
out_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\scripts\c21_cards.txt'

with open(html_path, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

prices = soup.find_all(string=lambda s: s and s.strip().startswith('$'))
cards = []

for p in prices:
    parent = p.parent
    while parent and parent.name != 'body':
        if parent.name == 'div' and parent.get('class') and any('property' in c for c in parent.get('class')):
            # Let's see if it's the main wrapper
            if 'property-card' in parent.get('class') or 'property-list' in parent.get('class') or parent.find('a', href=True):
                if parent not in cards:
                    cards.append(parent)
                break
        parent = parent.parent

with open(out_path, 'w', encoding='utf-8') as f:
    if cards:
        f.write(f"Found {len(cards)} cards based on price.\n\n")
        f.write(cards[0].prettify())
    else:
        f.write("No cards found.")

print(f"Found {len(cards)} cards.")
