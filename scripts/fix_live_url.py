import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_001_LISTING.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

# Update live_url based on the HTML's base href
data['live_url'] = "https://www.century21.com/homes/list/city/ca/san-francisco"

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated live_url.")
