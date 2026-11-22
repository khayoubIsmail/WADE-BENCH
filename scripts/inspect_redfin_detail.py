import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

print("H1 Title:", soup.find('h1').get_text(strip=True) if soup.find('h1') else None)

def print_text_match(text):
    import re
    el = soup.find(string=re.compile(text, re.IGNORECASE))
    if el:
        print(f"Found '{text}' in {el.parent.name} with class {el.parent.get('class')}")
        return el
    print(f"'{text}' not found")
    return None

print_text_match('Price')
print_text_match('Status')
print_text_match('Type')
print_text_match('Year built')
print_text_match('Lot size')
print_text_match('Price/Sq.Ft.')
print_text_match('Listed by')
print_text_match('About this home')
print_text_match('Property details')
print_text_match('Public record')
print_text_match('Around this home')

