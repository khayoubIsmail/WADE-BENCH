import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Find area "515m" in DOM
print("=== Area 515m ===")
for el in soup.find_all(string=lambda t: t and '515' in t):
    if el.parent.name not in ['script', 'style']:
        print("  area:", el.parent.name, el.parent.get('class'), '|', repr(el.strip()[:60]))

# Find bedroom count (integer 4 next to bed icon)
print("=== Beds/baths icons ===")
for el in soup.find_all('span', attrs={'data-test': True}):
    print("  data-test span:", el.get('data-test'), '|', el.get_text(strip=True))

# Find property type "House"
print("=== Property type ===")
for el in soup.find_all(string=lambda t: t and t.strip() == 'House'):
    if el.parent.name not in ['script', 'style']:
        print("  House:", el.parent.name, el.parent.get('class'))

# Find agent name
print("=== Agent branding name ===")
for el in soup.find_all(string=lambda t: t and 'Harcourts' in t):
    if el.parent.name not in ['script', 'style']:
        print("  Office:", el.parent.name, el.parent.get('class'), '|', el.strip()[:60])

# Find aria-label for beds/baths
print("=== Aria labels ===")
for el in soup.find_all(attrs={'aria-label': True}):
    label = el.get('aria-label', '').lower()
    if 'bed' in label or 'bath' in label or 'car' in label:
        print("  aria-label:", el.get('aria-label'), '| text:', el.get_text(strip=True)[:40])
