import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Load state data
state_script = None
for s in soup.find_all('script'):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        state_script = s
        break
data = json.loads(state_script.string)
for qv in data.get('queries', {}).values():
    try:
        q_data = json.loads(qv)
        listings = q_data.get('data', [])
        if listings:
            attr = listings[0].get('attributes', {})
            title = attr.get('header')
            location = attr.get('address', {}).get('display-address')
            beds = attr.get('bedroom-count')
            baths = attr.get('bathroom-count')
            area = str(attr.get('land-area', '')) + 'm'
            prop_type = attr.get('listing-sub-type')
            print(f"title={title}, location={location}, beds={beds}, baths={baths}, area={area}, type={prop_type}")
            break
    except Exception as e:
        print('error:', e)

# Now find these in DOM
print()
print("=== DOM searches ===")

# Title
for el in soup.find_all(string=lambda t: t and 'Ticket to Rototuna' in t):
    if el.parent.name not in ['script', 'style']:
        print("title:", el.parent.name, el.parent.get('class'), '|', el.strip()[:60])

# Location "9 Woodham Place, Rototuna North"
for el in soup.find_all(string=lambda t: t and 'Rototuna North' in t):
    if el.parent.name not in ['script', 'style']:
        print("location:", el.parent.name, el.parent.get('class'), '|', el.strip()[:80])

# Bedrooms (look for number near a bedroom icon/text)
for el in soup.find_all(string=lambda t: t and t.strip() == '4'):
    if el.parent.name not in ['script', 'style']:
        gp = el.parent.parent
        gp_text = gp.get_text() if gp else ''
        if 'bed' in gp_text.lower():
            print("beds:", el.parent.name, el.parent.get('class'), '|', gp.get_text(strip=True)[:60])
