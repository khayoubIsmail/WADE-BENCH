import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

print("H1 title:", soup.find('h1').get_text(strip=True) if soup.find('h1') else None)

def find_by_text(text):
    for el in soup.find_all(string=re.compile(text, re.IGNORECASE)):
        print(f"Found text '{text}' in:", el.parent.name, el.parent.get('class'))

# The JSON says listing_title = "12B Mary Street, Papanui"
# Check if price is mentioned
print("Price:")
find_by_text(r'\$')

# Check beds, baths, floor, land, parking
print("\nFeatures:")
find_by_text('Bed')
find_by_text('Bath')
find_by_text('Floor area')
find_by_text('Land area')
find_by_text('Park')
find_by_text('Garage')

# Check images
print("\nImages:")
for img in soup.find_all('img')[:5]:
    print(img.get('src'))

# Check dates
print("\nDates:")
find_by_text('published')
