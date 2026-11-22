import json
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_APARTMENTS_002_DETAIL\page.html'
data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(html_path, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
gallery_images = []
carousel = soup.find('div', class_='owl-carousel', attrs={'data-photocount': True})
if carousel:
    for img in carousel.find_all('img'):
        src = img.get('data-src') or img.get('src')
        if src:
            src = src.split(' ')[0]
            gallery_images.append(src)

final_images = list(dict.fromkeys(gallery_images))

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

data['records'][0]['fields']['images_urls']['value'] = final_images
data['records'][0]['fields']['images_urls']['normalized'] = final_images

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Updated JSON with exactly {len(final_images)} images.")
