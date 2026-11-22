import sys; sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
soup=BeautifulSoup(open(r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_LEBONCOIN_001_LISTING\page.html', encoding='utf-8').read(), 'html.parser')

articles = soup.find_all('article')
# Real listings only (skip promo card with no aria-label matching properties)
real_cards = [a for a in articles if a.get('aria-label') and ('pièces' in a.get('aria-label','') or 'pièce' in a.get('aria-label','') or 'm²' in a.get('aria-label',''))]
print('Real listing cards:', len(real_cards))

c = real_cards[0]
# Extract key elements
link_el = c.find('a', href=lambda x: x and '/ad/ventes_immobilieres/' in x)
print('URL:', link_el['href'] if link_el else None)
print('aria-label:', c.get('aria-label'))

# Find price
all_spans = [s for s in c.find_all(['p','span','div']) if s.text.strip() and not s.find(['p','span','div'])]
for s in all_spans[:20]:
    print(repr(s.text.strip()), '|', s.name, '|', str(s.get('class',''))[:60])
