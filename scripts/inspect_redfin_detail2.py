import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

def print_key_value():
    key_vals = soup.find_all('div', class_='keyDetail')
    if key_vals:
        print("\n--- Key Details ---")
        for kv in key_vals:
            print(kv.get_text(" ", strip=True))

print_key_value()

print("\n--- Main stats ---")
stats = soup.find('div', {'data-rf-test-id': 'abp-homeinfo-home-stats'})
if stats:
    print(stats.get_text(" | ", strip=True))
else:
    stats = soup.find('div', class_='home-main-stats')
    if stats: print(stats.get_text(" | ", strip=True))

print("\n--- Sections ---")
sections = ['About this home', 'Around this home', 'Property details', 'Public record']
for sec in sections:
    el = soup.find(string=lambda t: t and sec.lower() in t.lower())
    if el:
        p = el.parent
        while p and p.name != 'div' and p.name != 'section':
            p = p.parent
        if p:
            print(f"[{sec}] Container HTML sample:", str(p)[:200].encode('ascii', 'ignore').decode())

