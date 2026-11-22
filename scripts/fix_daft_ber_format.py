import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_DAFT.IE_001_LISTING.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

for record in data['records']:
    # Fix BER value
    if 'BER_energy_rating' in record['fields']:
        val = record['fields']['BER_energy_rating']['value']
        norm = record['fields']['BER_energy_rating']['normalized']
        
        # If it doesn't already start with BER, prepend it for value
        if not val.startswith("BER "):
            record['fields']['BER_energy_rating']['value'] = f"BER {val}"
            
    # Fix provenance listing_url text_quote if needed
    if 'listing_url' in record['provenance']:
        tq = record['provenance']['listing_url'].get('text_quote', '')
        if tq.startswith("https://www.daft.iehttps://www.daft.ie"):
            record['provenance']['listing_url']['text_quote'] = tq.replace("https://www.daft.iehttps://www.daft.ie", "https://www.daft.ie")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Fixed BER formatting and provenance listing_url.")
