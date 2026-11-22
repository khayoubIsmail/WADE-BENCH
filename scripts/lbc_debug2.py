import sys; sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
soup=BeautifulSoup(open(r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_LEBONCOIN_001_LISTING\page.html', encoding='utf-8').read(), 'html.parser')

articles = soup.find_all('article')
print(f'Total articles: {len(articles)}')

for i, a in enumerate(articles):
    link = a.find('a', href=lambda x: x and '/ad/' in x)
    title = a.get('aria-label')
    if not title:
        title = a.text.strip()[:30].replace('\n', ' ')
    print(f"Article {i}: {link['href'] if link else 'No link'} | {title}")
