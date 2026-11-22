import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "Total Bathrooms": {
        "value": "3",
        "normalized": 3
    },
    "Full Bathrooms": {
        "value": "2",
        "normalized": 2
    },
    "Half Bathrooms": {
        "value": "1",
        "normalized": 1
    },
    "Bathroom Features": {
        "value": "Closet, Marble, Tile, Tub w/Shower Over, Window",
        "normalized": ["Closet", "Marble", "Tile", "Tub w/Shower Over", "Window"]
    },
    "Primary Bathroom": {
        "value": "Jetted Tub, Marble, Tile",
        "normalized": ["Jetted Tub", "Marble", "Tile"]
    },
    "Total Bedrooms": {
        "value": "4",
        "normalized": 4
    },
    "Primary Bedroom": {
        "value": "Sitting Area, Walk-In Closet",
        "normalized": ["Sitting Area", "Walk-In Closet"]
    },
    "Bedroom 1": {
        "value": "Sitting Area, Walk-In Closet",
        "normalized": ["Sitting Area", "Walk-In Closet"]
    },
    "Kitchen": {
        "value": "Breakfast Area, Marble Counter, Pantry Closet",
        "normalized": ["Breakfast Area", "Marble Counter", "Pantry Closet"]
    },
    "Dining Room": {
        "value": "Formal Room",
        "normalized": "Formal Room"
    },
    "Laundry": {
        "value": "Inside Room, Inside Room",
        "normalized": "Inside Room"
    }
}

new_provenance = {
    "Total Bathrooms": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "3"
    },
    "Full Bathrooms": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "2"
    },
    "Half Bathrooms": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "1"
    },
    "Bathroom Features": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Closet, Marble, Tile, Tub w/Shower Over, Window"
    },
    "Primary Bathroom": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Jetted Tub, Marble, Tile"
    },
    "Total Bedrooms": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "4"
    },
    "Primary Bedroom": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Sitting Area, Walk-In Closet"
    },
    "Bedroom 1": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Sitting Area, Walk-In Closet"
    },
    "Kitchen": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Breakfast Area, Marble Counter, Pantry Closet"
    },
    "Dining Room": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Formal Room"
    },
    "Laundry": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Inside Room, Inside Room"
    }
}

# Optional cleanup: if the user previously had `bathrooms_full`, `bedrooms`, etc. 
# we might want to pop them to prevent duplication.
keys_to_remove = ["bathrooms_full", "bathrooms_half", "bedrooms"]
for k in keys_to_remove:
    data['records'][0]['fields'].pop(k, None)
    data['records'][0]['provenance'].pop(k, None)

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested room/bathroom fields.")
