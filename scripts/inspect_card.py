import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Find all h4s that contain 'Rototuna'
for h4 in soup.find_all('h4'):
    if 'Rototuna' in h4.get_text():
        print("Found h4:", h4)
        card_a = h4.find_parent('a')
        if card_a:
            print("href:", card_a.get('href'))
            print(card_a.prettify()[:4000])
        break
