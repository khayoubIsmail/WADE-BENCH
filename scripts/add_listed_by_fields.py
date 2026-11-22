import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "Listed by": {
        "value": "Berkshire Hathaway-Franciscan, Andrew Herrera II",
        "normalized": "Berkshire Hathaway-Franciscan, Andrew Herrera II"
    },
    "Listing Office": {
        "value": "Berkshire Hathaway-Franciscan",
        "normalized": "Berkshire Hathaway-Franciscan"
    },
    "Listing Agent": {
        "value": "Andrew Herrera II",
        "normalized": "Andrew Herrera II"
    }
}

new_provenance = {
    "Listed by": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "p.mls-idx",
        "xpath": "//*[@id='full-property-detail-body']//p[contains(@class,'mls-idx')]",
        "text_quote": "Berkshire Hathaway-Franciscan, Andrew Herrera II"
    },
    "Listing Office": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "span.office-name",
        "xpath": "//*[@id='full-property-detail-body']//span[contains(@class,'office-name')]",
        "text_quote": "Berkshire Hathaway-Franciscan"
    },
    "Listing Agent": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "span.attr-idx",
        "xpath": "//*[@id='full-property-detail-body']//span[contains(@class,'attr-idx')]",
        "text_quote": "Andrew Herrera II"
    }
}

keys_to_remove = ["listing_agent", "listing_office", "listing_agent_license"]
for k in keys_to_remove:
    data['records'][0]['fields'].pop(k, None)
    data['records'][0]['provenance'].pop(k, None)

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested agent and office fields.")
