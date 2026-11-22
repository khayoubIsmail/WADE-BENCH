import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for r in data['records']:
    print("Record ID:", r['gold_record_id'])
    for k, v in r['provenance'].items():
        print(f"{k}:")
        print(f"  css: {v['css_selector']}")
        print(f"  xpath: {v['xpath']}")
    break
