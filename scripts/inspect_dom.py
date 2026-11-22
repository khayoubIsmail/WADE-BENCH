import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Find the state script
for idx, s in enumerate(soup.find_all('script')):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        print(f"State script index: {idx}")
        print(f"Script id: {s.get('id')}")
        print(f"Script classes: {s.get('class')}")
        break

# Check what is visible in the DOM for listing 1
print()
# look for bedrooms
for el in soup.find_all(string=lambda t: t and '4' == t.strip()):
    p = el.parent
    if p.name in ['span', 'div', 'strong']:
        gp = p.parent
        if gp:
            gp_text = gp.get_text(strip=True).lower()
            if 'bed' in gp_text:
                print('Found bedroom:', el.strip(), '| parent:', p.name, p.get('class'))

# look for title "Ticket to Rototuna"
print()
for el in soup.find_all(string=lambda t: t and 'Ticket to Rototuna' in t):
    if el.parent.name not in ['script', 'style']:
        print('Title found in:', el.parent.name, el.parent.get('class'))
