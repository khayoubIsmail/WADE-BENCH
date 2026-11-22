import json
import re
import glob
from bs4 import BeautifulSoup

def get_element_from_xpath(soup, xpath):
    if not xpath: return None
    components = xpath.strip('/').split('/')
    if not components or components[0] == '': return None
    if components[0] == 'html': components = components[1:]
    curr = soup.find('html') or soup
    for comp in components:
        m = re.match(r'([a-zA-Z0-9\-]+)(?:\[(\d+)\])?', comp)
        if not m: return None
        tag = m.group(1)
        idx = int(m.group(2)) - 1 if m.group(2) else 0
        children = curr.find_all(tag, recursive=False)
        if idx < len(children):
            curr = children[idx]
        else:
            return None
    return curr

def build_css_selector(el):
    if not el: return ""
    
    def get_stable_attr(node):
        if not node or not hasattr(node, 'get'): return None
        if node.get('itemprop'): return f'{node.name}[itemprop="{node.get("itemprop")}"]'
        if node.get('data-tracking'): return f'{node.name}[data-tracking="{node.get("data-tracking")}"]'
        if node.get('data-testid'): return f'{node.name}[data-testid="{node.get("data-testid")}"]'
        
        node_id = node.get('id')
        if node_id and isinstance(node_id, str): 
            if len(node_id) < 30 and not re.search(r'\d{6}', node_id):
                return f'{node.name}#{node_id}'
        
        classes = node.get('class', [])
        if isinstance(classes, str): classes = classes.split()
        # Exclude very generic layout classes
        valid_classes = [c for c in classes if len(c) > 2 and not c.startswith('sc-') and c not in ['flex', 'col', 'row', 'container', 'wrapper', 'item', 'list']]
        if valid_classes:
            return f'{node.name}.{valid_classes[0]}'
        return None

    path = []
    curr = el
    while curr and curr.name not in ['body', 'html', '[document]']:
        attr = get_stable_attr(curr)
        if attr:
            # We found a stable scoped parent/element
            if path:
                return f"{attr} > " + " > ".join(path[::-1])
            else:
                return attr
        
        # Determine nth-of-type if there are siblings of same tag
        siblings = curr.find_previous_siblings(curr.name)
        if siblings:
            path.append(f"{curr.name}:nth-of-type({len(siblings) + 1})")
        else:
            path.append(curr.name)
        curr = curr.parent

    if path:
        return " > ".join(path[::-1])
    return el.name if el.name else ""

files_to_fix = [
    r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_001_LISTING.json',
    r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json',
    r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_001_LISTING.json',
    r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_002_DETAIL.json'
]

for f_path in files_to_fix:
    with open(f_path, encoding='utf-8') as f:
        data = json.load(f)
        
    snap_id = "SNAP_" + f_path.split('\\')[-1].replace("WBV1_", "").replace(".json", "")
    html_path = rf'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\{snap_id}\page.html'
    try:
        soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
    except Exception as e:
        print(f"Error loading {html_path}: {e}")
        continue
        
    for record in data['records']:
        for k, prov in record.get('provenance', {}).items():
            if 'snapshot_id' not in prov: continue
            prov['snapshot_id'] = snap_id
                
            xpath = prov.get('xpath')
            if not xpath: continue
            
            el = get_element_from_xpath(soup, xpath)
            if el:
                new_css = build_css_selector(el)
                if new_css:
                    prov['css_selector'] = new_css

    with open(f_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Fixed", f_path.split('\\')[-1])
