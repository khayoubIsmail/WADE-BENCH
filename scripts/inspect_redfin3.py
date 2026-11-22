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

for card in cards[:3]:
    print("\n--- Card ---")
    # Link
    a = card.find('a')
    if a: print("URL:", a.get('href'))
    
    # Image
    img = card.find('img')
    if img: print("Image:", img.get('src'))
    
    # Price
    price = card.find('span', class_='bp-Homecard__Price--value')
    if price: print("Price:", price.get_text(strip=True))
    
    # Address/Location
    addr = card.find('div', class_='bp-Homecard__Address')
    if addr: print("Location:", addr.get_text(strip=True))
    
    # Stats (beds, baths, sqft)
    stats = card.find_all('div', class_='bp-Homecard__Stat')
    for stat in stats:
        print("Stat:", stat.get_text(" ", strip=True))
        
    # Sashes (open time, new)
    sashes = card.find_all('span', class_='bp-Homecard__Sash')
    for s in sashes:
        print("Sash:", s.get_text(strip=True))
        
    # Features
    features = card.find('div', class_='KeyFactsExtension')
    if features:
        print("Features:", [f.strip() for f in features.get_text(strip=True).split('•') if f.strip()])
        
    # Listed by
    attribution = card.find('div', class_='bp-Homecard__Attribution')
    if attribution:
        print("Listed by:", attribution.get_text(strip=True))

