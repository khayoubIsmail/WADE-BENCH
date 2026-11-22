import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_DAFT.IE_001_LISTING.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

for record in data['records']:
    if 'listing_url' in record['fields']:
        val = record['fields']['listing_url']['value']
        if val.startswith("https://www.daft.iehttps://www.daft.ie"):
            val = val.replace("https://www.daft.iehttps://www.daft.ie", "https://www.daft.ie")
            record['fields']['listing_url']['value'] = val
            record['fields']['listing_url']['normalized'] = val

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Fixed listing_url in all records.")
