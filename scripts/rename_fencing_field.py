import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

old_key = 'Fencing (Description)'
new_key = 'FencingDescription'

fields = data['records'][0]['fields']
provenance = data['records'][0]['provenance']

if old_key in fields:
    fields[new_key] = fields.pop(old_key)

if old_key in provenance:
    provenance[new_key] = provenance.pop(old_key)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Renamed key successfully.")
