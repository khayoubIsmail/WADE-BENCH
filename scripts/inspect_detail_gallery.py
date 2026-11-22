import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

state_scripts = [s.string for s in soup.find_all('script') if s.string and 'self.__next_f.push' in s.string]

images = []
# Let's try to find a list of photos for the current listing.
for s in state_scripts:
    # Next.js state is complex. Let's look for "photos":[{"base-url":"/listings/42608006/..."
    # or just look for the first image we found in the DOM: 42608006
    # Is there a list of them?
    if '42608006' in s:
        # let's extract all base-urls that belong to this listing ID
        matches = re.findall(r'"base-url":"(/listings/42608006/[^"]+)"', s)
        for m in matches:
            if m not in images:
                images.append(m)
        
        # Alternatively, sometimes it's "baseUrl" instead of "base-url"
        matches2 = re.findall(r'"baseUrl":"(/listings/42608006/[^"]+)"', s)
        for m in matches2:
            if m not in images:
                images.append(m)

        # What if it's "image":{"baseUrl":"..."}
        
print("Images for 42608006:")
for img in images:
    print(img)
    
if not images:
    print("No images found with base-url regex. Let's dump the script parts containing 42608006.")
    for s in state_scripts:
        if '42608006' in s:
            # find the index
            idx = s.find('42608006')
            print(s[max(0, idx-200):idx+500])
