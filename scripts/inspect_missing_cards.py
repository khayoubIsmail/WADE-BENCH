import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

# Load JSON state to get listings 15-20 URLs
for s in soup.find_all('script'):
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data = json.loads(s.string)
        for qv in data.get('queries', {}).values():
            try:
                q_data = json.loads(qv)
                listings = q_data.get('data', [])
                if len(listings) >= 15:
                    for listing in listings[14:]:
                        attr = listing.get('attributes', {})
                        url = attr.get('website-full-url', '')
                        slug = url.replace('https://www.realestate.co.nz', '')
                        title = attr.get('header', '')
                        # Try to find card
                        found = None
                        for a in soup.find_all('a', href=True):
                            if slug in a.get('href', ''):
                                found = a
                                break
                        if found:
                            has_h4 = bool(found.find('h4'))
                            # What headings does it have?
                            headings = [t.name for t in found.find_all(['h1','h2','h3','h4','h5','h6'])]
                            print(f"URL: {slug[:50]} | title: {title[:30]} | has_h4: {has_h4} | headings: {headings}")
                        else:
                            print(f"URL: {slug[:50]} | title: {title[:30]} | NOT FOUND IN DOM")
            except Exception as e:
                print('err:', e)
        break
