import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "For Sale": {
        "value": "Yes",
        "normalized": True
    },
    "Association Fee": {
        "value": "$27",
        "normalized": {"amount": 27, "currency": "USD"}
    },
    "Assoc Fee Freq.": {
        "value": "Annually",
        "normalized": "annually"
    },
    "Special Conditions": {
        "value": "Standard",
        "normalized": "Standard"
    },
    "APN": {
        "value": "3041017",
        "normalized": "3041017"
    }
}

new_provenance = {
    "For Sale": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Yes"
    },
    "Association Fee": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "$27"
    },
    "Assoc Fee Freq.": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Annually"
    },
    "Special Conditions": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Standard"
    },
    "APN": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "3041017"
    }
}

keys_to_remove = ["association_fee", "association_fee_frequency", "special_conditions", "apn"]
for k in keys_to_remove:
    data['records'][0]['fields'].pop(k, None)
    data['records'][0]['provenance'].pop(k, None)

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested financial and disclosure fields.")
