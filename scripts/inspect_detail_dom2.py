import json
from bs4 import BeautifulSoup
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_REALESTATE.CO.NZ_002_DETAIL\page.html'
soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')

print("Title:", soup.find('h1').get_text(strip=True) if soup.find('h1') else None)

# Print all text in the main container
main = soup.find('main')
if main:
    for text in main.stripped_strings:
        print(text)
else:
    print("No <main> tag found")

print("\n--- Next.js state data extraction ---")
state_scripts = []
for s in soup.find_all('script'):
    if s.string and 'self.__next_f.push' in s.string:
        state_scripts.append(s.string)

import ast
import json

for s in state_scripts:
    if 'Listing: Bathrooms: ' in s:
        # It's in the fbq or something similar
        match = re.search(r'Listing: Bathrooms: (\d+);Listing: Bedrooms: (\d+);Listing: Floor Area: (\d+);.*?Listing: Land Area: ([\d\sA-Z]+)', s)
        if match:
            print("Found in script via regex:", match.groups())

    if '"listing":' in s:
        # let's try to extract JSON parts
        matches = re.findall(r'(\[1,"[0-9a-f]+:(.*?)\]\n"\)', s)
        # It's tricky to parse Next.js chunks. Let's just regex for the data
        pass

