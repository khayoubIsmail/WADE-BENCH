import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

print("Images in DOM:")
count = 0
for btn in soup.find_all('button'):
    if btn.get('class') and 'media__photo' in btn.get('class'):
        img = btn.find('img')
        if img and img.get('src'):
            print(img.get('src'))
            count += 1
print(f"Total images in DOM: {count}")

print("\nLooking for images in scripts:")
script_imgs = []
for s in soup.find_all('script'):
    if s.string:
        # Looking for things like /listings/.../something.jpg
        # Since Next.js state has escaped JSON, we might see base-url or something
        matches = re.findall(r'/listings/[^"\\]+', s.string)
        if matches:
            script_imgs.extend(matches)

# Dedup and print
script_imgs = list(set(script_imgs))
for img in script_imgs[:10]:
    print(img)
print(f"Total unique listing images found in scripts: {len(script_imgs)}")

