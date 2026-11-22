import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

cards = soup.find_all('div', class_=re.compile('MapHomeCardReact'))
if not cards:
    cards = soup.find_all('div', class_=re.compile('HomeCardContainer'))
if not cards:
    cards = soup.find_all('div', class_='HomeCard')

card = cards[0]
for el in card.find_all('div'):
    text = el.get_text(" ", strip=True)
    if 'beds' in text.lower() or 'baths' in text.lower() or 'sq ft' in text.lower() or 'ave,' in text.lower():
        print("Match:", repr(text), "Class:", el.get('class'))
