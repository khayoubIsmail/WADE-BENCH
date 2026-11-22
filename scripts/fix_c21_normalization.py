import json
import re

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_001_LISTING.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

for record in data['records']:
    fields = record['fields']
    provenance = record['provenance']
    
    # Fix Open_House_time normalization
    if 'Open_House_time' in fields:
        val = fields['Open_House_time']['value']
        m = re.match(r"Open\s+([A-Za-z]+),\s+(.*?)\s+to\s+(.*)", val)
        if m:
            fields['Open_House_time']['normalized'] = {
                "day": m.group(1),
                "timing_start": m.group(2),
                "time_end": m.group(3)
            }
        else:
            fields['Open_House_time']['normalized'] = None

    # Fix price normalization
    if 'price' in fields:
        val = fields['price']['value']
        # remove '$', ',', and spaces
        clean_val = val.replace('$', '').replace(',', '').strip()
        try:
            fields['price']['normalized'] = int(clean_val)
        except ValueError:
            fields['price']['normalized'] = clean_val
            
    # Rename baths to bathrooms
    if 'baths' in fields:
        fields['bathrooms'] = fields.pop('baths')
    if 'baths' in provenance:
        provenance['bathrooms'] = provenance.pop('baths')

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Formatting applied successfully.")
