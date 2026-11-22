import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "Garage": {
        "value": "Yes",
        "normalized": True
    },
    "Garage Spaces": {
        "value": "2",
        "normalized": 2
    },
    "Parking Features": {
        "value": "Driveway, Attached, Covered, Enclosed, Garage Faces Front, Inside Entrance, Side by Side, On Site (Single Family Only)",
        "normalized": ["Driveway", "Attached", "Covered", "Enclosed", "Garage Faces Front", "Inside Entrance", "Side by Side", "On Site"]
    }
}

new_provenance = {
    "Garage": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Yes"
    },
    "Garage Spaces": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "2"
    },
    "Parking Features": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Driveway, Attached, Covered, Enclosed, Garage Faces Front, Inside Entrance, Side by Side, On Site (Single Family Only)"
    }
}

# Remove legacy lowercase keys
keys_to_remove = ["garage_spaces"]
for k in keys_to_remove:
    data['records'][0]['fields'].pop(k, None)
    data['records'][0]['provenance'].pop(k, None)

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested parking fields.")
