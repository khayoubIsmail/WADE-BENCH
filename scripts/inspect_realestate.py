import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_001_LISTING\page.html'
with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

scripts = soup.find_all('script')
data_str = None
for s in scripts:
    if s.string and '"created":' in s.string and '"queries":' in s.string:
        data_str = s.string
        break

if data_str:
    data = json.loads(data_str)
    queries = data.get('queries', {})
    for qk, qv in queries.items():
        if 'page[limit]=20' in qk:
            q_data = json.loads(qv)
            listings = q_data.get('data', [])
            included = {i['id']: i for i in q_data.get('included', [])}
            
            first = listings[0]
            attr = first.get('attributes', {})
            rel = first.get('relationships', {})
            
            print('photos count:', len(attr.get('photos', [])))
            print('listing_url:', attr.get('website-full-url'))
            print('location:', attr.get('address'))
            print('header:', attr.get('header'))
            print('title-type:', attr.get('title-type'))
            print('price:', attr.get('price-display'))
            print('beds:', attr.get('bedroom-count'))
            print('baths:', attr.get('bathroom-count'), attr.get('bathrooms-total-count'))
            print('floor area:', attr.get('floor-area'), attr.get('floor-area-unit'))
            print('land area:', attr.get('land-area'), attr.get('land-area-unit'))
            print('property_type:', attr.get('listing-category-code'))
            print('features:', attr.get('features'))
            
            agent_ids = [a['id'] for a in rel.get('agents', {}).get('data', [])]
            for aid in agent_ids:
                agent = included.get(aid, {}).get('attributes', {})
                print('agent name:', agent.get('first-name'), agent.get('last-name'))
                print('agent pic:', agent.get('photo-url'))
                
            office_ids = [o['id'] for o in rel.get('offices', {}).get('data', [])]
            for oid in office_ids:
                office = included.get(oid, {}).get('attributes', {})
                print('office name:', office.get('name'))
                print('office logo:', office.get('logo-url'))
            break
