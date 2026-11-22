import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open(r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_LEBONCOIN_001_LISTING.json', encoding='utf-8'))
for i in [0, 13]:
    print(f'--- Record {i+1} ---')
    record = data['records'][i]
    for k, v in record['fields'].items():
        print(f"{k}: {v['value']} ({v['normalized']})")
        css = record['provenance'][k]['css_selector']
        print(f"  CSS: {css}")
