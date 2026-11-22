import json
from bs4 import BeautifulSoup
import re

def get_xpath(element):
    if not element:
        return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]':
            break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            try:
                index = siblings.index(child) + 1
                components.append(f"{child.name}[{index}]")
            except ValueError:
                components.append(child.name)
        child = parent
    components.reverse()
    return f"/{'/'.join(components)}"

def process_file(json_path, html_path, is_list):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
        
    cards = soup.select('li.container-card') if is_list else [soup]
    
    for i, record in enumerate(data['records']):
        if is_list and i < len(cards):
            card = cards[i]
        else:
            card = soup

        for key, prov in record.get('provenance', {}).items():
            if 'xpath' in prov and prov['xpath']:
                continue
                
            css = prov.get('css_selector')
            val = prov.get('text_quote', '')
            
            el = None
            if css:
                # Need to handle :contains pseudoclass which is not standard BS4
                if ':contains' in css:
                    text_match = re.search(r':contains\("(.*?)"\)', css)
                    if text_match:
                        match_text = text_match.group(1)
                        base_css = css.split(':contains')[0]
                        candidates = card.select(base_css) if base_css else card.find_all(string=lambda s: s and match_text in s)
                        for c in candidates:
                            if hasattr(c, 'text') and match_text in c.text:
                                el = c
                                break
                            elif isinstance(c, str) and match_text in c:
                                el = c.parent
                                break
                else:
                    candidates = card.select(css)
                    if len(candidates) == 1:
                        el = candidates[0]
                    elif len(candidates) > 1:
                        # Try to match text
                        for c in candidates:
                            if val and val[:10] in c.text:
                                el = c
                                break
                        if not el:
                            el = candidates[0]
            if not el and val:
                # Find by text
                text_node = card.find(string=lambda s: s and val[:15] in s)
                if text_node:
                    el = text_node.parent
            
            if el:
                prov['xpath'] = get_xpath(el)
            else:
                prov['xpath'] = None

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

base = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench'

process_file(
    f"{base}\\data\\gold\\by_task\\realestate\\WBV1_REAL_CENTURY_21_001_LISTING.json",
    f"{base}\\data\\raw_snapshots\\realestate\\SNAP_REAL_CENTURY_21_001_LISTING\\page.html",
    is_list=True
)

process_file(
    f"{base}\\data\\gold\\by_task\\realestate\\WBV1_REAL_CENTURY_21_002_DETAIL.json",
    f"{base}\\data\\raw_snapshots\\realestate\\SNAP_REAL_CENTURY_21_002_DETAIL\\page.html",
    is_list=False
)

print("Added xpaths to both files.")
