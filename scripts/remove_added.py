import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_002_DETAIL.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

for record in data['records']:
    if 'Added' in record.get('fields', {}):
        del record['fields']['Added']
    if 'Added' in record.get('provenance', {}):
        del record['provenance']['Added']

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Removed 'Added' field.")
