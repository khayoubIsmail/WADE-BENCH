import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_CENTURY_21_002_DETAIL\page.html'
with open(html_path, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print(soup.title.text if soup.title else 'No Title')

# Look for basic facts (price, beds, baths)
price = soup.find(string=lambda s: s and '$' in s)
print(f"Price: {price.strip() if price else 'None'}")

# Dump the list of elements that look like keys in the facts
facts = soup.find_all('li')
fact_texts = []
for f in facts:
    text = f.get_text(separator=' ', strip=True)
    if ':' in text or len(text) < 50:
        fact_texts.append(text)

print("\n--- Potential Facts ---")
print('\n'.join(fact_texts[:30]))
