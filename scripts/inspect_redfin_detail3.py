import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REDFIN_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

with open('debug_detail.txt', 'w', encoding='utf-8') as f:
    def write_line(line):
        f.write(line + '\n')
        
    write_line("--- Price ---")
    price = soup.find('div', {'data-rf-test-id': 'abp-price'})
    if price: write_line("Price: " + price.get_text(strip=True))

    write_line("\n--- Beds, Baths, Sqft ---")
    beds = soup.find('div', {'data-rf-test-id': 'abp-beds'})
    baths = soup.find('div', {'data-rf-test-id': 'abp-baths'})
    sqft = soup.find('div', {'data-rf-test-id': 'abp-sqFt'})
    if beds: write_line("Beds: " + beds.get_text(strip=True))
    if baths: write_line("Baths: " + baths.get_text(strip=True))
    if sqft: write_line("Sqft: " + sqft.get_text(strip=True))
    
    write_line("\n--- Location ---")
    # In redfin detail pages, the street address is usually in an h1 or some div
    street = soup.find('div', class_='street-address')
    city = soup.find('div', class_='dp-subtext')
    if street: write_line("Street: " + street.get_text(strip=True))
    if city: write_line("City: " + city.get_text(strip=True))
    
    # Try just printing all h1/h2
    for h in soup.find_all('h1'): write_line("H1: " + h.get_text(strip=True))
    for h in soup.find_all('h2'): write_line("H2: " + h.get_text(strip=True))

    write_line("\n--- Key Details ---")
    key_details = soup.find_all('div', class_='keyDetail')
    for kd in key_details:
        write_line("KeyDetail: " + kd.get_text(" | ", strip=True))

    write_line("\n--- Listed By ---")
    agent_info = soup.find_all('div', class_='agent-info-item')
    for ai in agent_info:
        write_line("Agent Info: " + ai.get_text(" | ", strip=True))
        
    for p in soup.find_all('p'):
        if 'Listed by' in p.get_text():
            write_line("Listed by P: " + p.get_text(strip=True))
