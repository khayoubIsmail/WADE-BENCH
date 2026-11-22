import json
import re

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_002_DETAIL.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

for record in data['records']:
    if 'Updated' in record.get('fields', {}):
        val = record['fields']['Updated']['value']
        
        # Split into date and time
        parts = val.split(' at ')
        normalized = {}
        if len(parts) == 2:
            normalized = {
                "date": parts[0].strip(),
                "time": parts[1].strip()
            }
        else:
            normalized = val
        
        record['fields']['published_or_posted'] = {
            "value": val,
            "normalized": normalized
        }
        del record['fields']['Updated']
        
    if 'Updated' in record.get('provenance', {}):
        record['provenance']['published_or_posted'] = record['provenance'].pop('Updated')

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Changed 'Updated' to 'published_or_posted' and normalized date/time.")
