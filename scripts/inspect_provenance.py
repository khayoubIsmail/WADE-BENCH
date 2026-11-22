import json
data = json.load(open(r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_REALESTATE.CO.NZ_001_LISTING.json', encoding='utf-8'))
rec = data['records'][0]
for k, v in rec['provenance'].items():
    css = v['css_selector']
    xpath = v['xpath']
    print(f"{k}:")
    print(f"  css: {css}")
    print(f"  xpath: {xpath}")
