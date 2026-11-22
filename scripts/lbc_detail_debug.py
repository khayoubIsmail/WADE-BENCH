import sys; sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
import json
soup=BeautifulSoup(open(r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_LEBONCOIN_002_DETAIL\page.html', encoding='utf-8').read(), 'html.parser')

print('--- Criteria (data-qa-id="criteria_item") ---')
for el in soup.find_all(attrs={'data-qa-id': 'criteria_item'}):
    texts = [t.text.strip() for t in el.find_all(['p', 'div']) if t.text.strip()]
    # Typically first is label, second is value
    # But sometimes structure is a bit nested
    print('ITEM:', ' | '.join(texts[:4]))
        
print('\n--- Price ---')
price_el = soup.find(attrs={'data-qa-id': 'adview_price'})
if price_el: print(price_el.text.strip())

print('\n--- Mensualités ---')
for p in soup.find_all('p'):
    if 'Mensualités' in p.text:
        print(p.text.strip())

print('\n--- Location ---')
loc_el = soup.find(attrs={'data-qa-id': 'adview_location_informations'})
if loc_el: print(loc_el.text.strip())

print('\n--- Description ---')
desc_el = soup.find(attrs={'data-qa-id': 'adview_description_container'})
if desc_el: print(desc_el.text.strip()[:100])
    
print('\n--- Agent ---')
# The "Vendu par" section
store_el = soup.find(attrs={'data-qa-id': 'store-contact'})
if store_el:
    print('Contact:', store_el.text.strip())
    # find logo
    img = store_el.find('img')
    if img: print('Logo:', img.get('src'))
    
print('\n--- Images ---')
for img in soup.find_all('img', alt='image-galerie'):
    print(img.get('src', '')[:60], img.get('data-src', '')[:60])
