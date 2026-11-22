import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_DAFT.IE_001_LISTING\page.html'
with open(html_path, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print(soup.title.text if soup.title else 'No Title')

# Daft usually uses li for properties or divs with specific data attributes
cards = soup.find_all('li', class_=lambda c: c and 'SearchCard' in c)
if not cards:
    cards = soup.find_all('div', attrs={"data-testid": "search-card"})
if not cards:
    cards = soup.find_all('li')

print(f"Found {len(cards)} potential property cards.")

if cards:
    card = cards[0]
    print("\n--- Card HTML snippet ---")
    print(card.prettify()[:1000])
