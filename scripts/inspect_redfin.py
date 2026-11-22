import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

print("Checking Redfin listing cards...")
cards = soup.find_all('div', class_=re.compile('MapHomeCardReact'))
if not cards:
    cards = soup.find_all('div', class_=re.compile('HomeCardContainer'))
if not cards:
    cards = soup.find_all('div', class_='HomeCard')

print(f"Found {len(cards)} cards")

if cards:
    card = cards[0]
    print("\n--- First Card HTML ---")
    print(str(card)[:1000].encode('ascii', 'ignore').decode())

    # Text
    print("\n--- Texts ---")
    for s in card.stripped_strings:
        print(s)

    print("\n--- Links ---")
    for a in card.find_all('a'):
        print(a.get('href'))
        
    print("\n--- Images ---")
    for img in card.find_all('img'):
        print(img.get('src'))

