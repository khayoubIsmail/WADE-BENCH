import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def print_element_context(text):
    el = soup.find(string=re.compile(text, re.IGNORECASE))
    if el and el.parent:
        p = el.parent
        print(f"\n--- Context for '{text}' ---")
        print("Parent:", p.name, p.get('class'))
        
        # usually these are in a flex or grid container next to their values
        container = p.parent
        print("Container:", container.name, container.get('class'))
        
        # let's print the siblings to see the value
        for sib in container.children:
            if sib.name:
                print("  Sibling:", sib.name, sib.get('class'), "->", sib.get_text(strip=True))

print_element_context('Bedroom')
print_element_context('Bathroom')
print_element_context('Floor area')
print_element_context('Land area')
print_element_context('Garage')
print_element_context('Estimate updated on')
print_element_context('\$786K')

# find image gallery
for btn in soup.find_all('button'):
    if btn.get('class') and 'media__photo' in btn.get('class'):
        img = btn.find('img')
        if img:
            print("\nImage found:", img.get('src'))

