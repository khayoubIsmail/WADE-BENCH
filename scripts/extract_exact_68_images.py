import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_APARTMENTS_002_DETAIL\page.html'
try:
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Method 1: Look for the owl-carousel that has the photos
    gallery_images = []
    carousel = soup.find('div', class_='owl-carousel', attrs={'data-photocount': True})
    if carousel:
        for img in carousel.find_all('img'):
            src = img.get('data-src') or img.get('src')
            if src:
                # keep only the first url if there's a space (like in srcset)
                src = src.split(' ')[0]
                gallery_images.append(src)
                
    # Remove duplicates but preserve order
    final_images = list(dict.fromkeys(gallery_images))
    print(f"Found {len(final_images)} images via owl-carousel.")
    
    # Method 2: Check the script tag for JSON data
    script = soup.find('script', id='json-pd-init')
    if script:
        content = script.string
        match = re.search(r'"Photos"\s*:\s*(\[[^\]]+\])', content)
        if match:
            try:
                photos = json.loads(match.group(1))
                print(f"Found {len(photos)} images in JSON script.")
            except:
                pass
except Exception as e:
    print(f"Error: {e}")
