import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "Area": {
        "value": "SF District 4",
        "normalized": "SF District 4"
    },
    "County": {
        "value": "San Francisco",
        "normalized": "San Francisco"
    },
    "Cross Streets": {
        "value": "Ravenswood Dr",
        "normalized": "Ravenswood Dr"
    }
}

new_provenance = {
    "Area": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "SF District 4"
    },
    "County": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "San Francisco"
    },
    "Cross Streets": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Ravenswood Dr"
    }
}

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested location fields.")
