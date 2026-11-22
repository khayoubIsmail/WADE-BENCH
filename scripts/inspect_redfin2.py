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

for card in cards:
    texts = list(card.stripped_strings)
    text_str = " ".join(texts)
    if 'OPEN' in text_str.upper() or 'SAT' in text_str.upper() or 'SUN' in text_str.upper():
        print("\n--- Card with open time? ---")
        print("Texts:", texts)
        
        # Let's see how features and listed_by are structured
        print("\nFeatures/Listed by structure:")
        for el in card.find_all('div'):
            if el.get_text(strip=True).startswith('Listing by'):
                print("Listed by:", el.get_text(strip=True), "Classes:", el.get('class'))
            elif '•' in el.get_text(strip=True):
                print("Features container:", el.get_text(strip=True), "Classes:", el.get('class'))
