import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_002_DETAIL.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

fields = data['records'][0]['fields']
provenance = data['records'][0]['provenance']

# Fix sq._ft.
if 'sq._ft.' in fields:
    fields['sq._ft.']['value'] = "2,300 sq. ft."
    fields['sq._ft.']['normalized'] = 2300
    
if 'sq._ft.' in provenance:
    provenance['sq._ft.']['text_quote'] = "2,300 sq. ft."

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Fixed sq._ft. field")
