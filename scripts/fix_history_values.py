import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

fields = data['records'][0]['fields']

if 'Price_&_Sales_History' in fields:
    fields['Price_&_Sales_History']['value'] = fields['Price_&_Sales_History']['normalized']

if 'Tax_History' in fields:
    fields['Tax_History']['value'] = fields['Tax_History']['normalized']

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Successfully replaced summary strings with actual arrays for history values.")
