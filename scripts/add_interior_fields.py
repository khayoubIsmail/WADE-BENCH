import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

# Fields to add based on user request:
new_fields = {
    "Number of Rooms": {
        "value": "8",
        "normalized": 8
    },
    "Rooms/Areas": {
        "value": "Bathroom, Dining Room, Home Theater, Living Room, Storage",
        "normalized": ["Bathroom", "Dining Room", "Home Theater", "Living Room", "Storage"]
    },
    "Interior Features": {
        "value": "Formal Entry, Storage",
        "normalized": ["Formal Entry", "Storage"]
    },
    "Fireplace": {
        "value": "Yes",
        "normalized": True
    },
    "Number of Fireplaces": {
        "value": "1",
        "normalized": 1
    },
    "Fireplace(s)": {
        "value": "Gas, Living Room",
        "normalized": ["Gas", "Living Room"]
    },
    "Appliances": {
        "value": "Dishwasher, Disposal, Gas Plumbed, Range Hood, Microwave, Dryer, Washer",
        "normalized": ["Dishwasher", "Disposal", "Gas Plumbed", "Range Hood", "Microwave", "Dryer", "Washer"]
    },
    "Flooring": {
        "value": "Marble, Tile, Wood",
        "normalized": ["Marble", "Tile", "Wood"]
    }
}

new_provenance = {
    "Number of Rooms": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "8"
    },
    "Rooms/Areas": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Bathroom, Dining Room, Home Theater, Living Room, Storage"
    },
    "Interior Features": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Formal Entry, Storage"
    },
    "Fireplace": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Yes"
    },
    "Number of Fireplaces": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "1"
    },
    "Fireplace(s)": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Gas, Living Room"
    },
    "Appliances": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Dishwasher, Disposal, Gas Plumbed, Range Hood, Microwave, Dryer, Washer"
    },
    "Flooring": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Marble, Tile, Wood"
    }
}

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested Interior fields.")
