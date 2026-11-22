import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "Property View": {
        "value": "City, City Lights, Golf Course, Hills, Lake, Ocean, Panoramic, Park/Greenbelt, San Francisco, Water",
        "normalized": ["City", "City Lights", "Golf Course", "Hills", "Lake", "Ocean", "Panoramic", "Park/Greenbelt", "San Francisco", "Water"]
    },
    "Lot Size (Acres)": {
        "value": "0.0733",
        "normalized": 0.0733
    },
    "Lot Size (Sq. Ft.)": {
        "value": "3,192",
        "normalized": 3192
    },
    "Street/Road Desc.": {
        "value": "Paved",
        "normalized": "Paved"
    },
    "Road Maintenance": {
        "value": "Public Maintained Road",
        "normalized": "Public Maintained Road"
    },
    "Lot Features": {
        "value": "Curb(s)/Gutter(s), Garden, Grass Artificial, Landscaped, Landscape Front, Landscape Misc, Street Lights",
        "normalized": ["Curb(s)/Gutter(s)", "Garden", "Grass Artificial", "Landscaped", "Landscape Front", "Landscape Misc", "Street Lights"]
    },
    "Fencing (Description)": {
        "value": "Back Yard, Fenced",
        "normalized": ["Back Yard", "Fenced"]
    }
}

new_provenance = {
    "Property View": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "City, City Lights, Golf Course, Hills, Lake, Ocean, Panoramic, Park/Greenbelt, San Francisco, Water"
    },
    "Lot Size (Acres)": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "0.0733"
    },
    "Lot Size (Sq. Ft.)": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "3,192"
    },
    "Street/Road Desc.": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Paved"
    },
    "Road Maintenance": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Public Maintained Road"
    },
    "Lot Features": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Curb(s)/Gutter(s), Garden, Grass Artificial, Landscaped, Landscape Front, Landscape Misc, Street Lights"
    },
    "Fencing (Description)": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Back Yard, Fenced"
    }
}

keys_to_remove = ["lot_size_acres", "lot_size_sqft", "lot_features"]
for k in keys_to_remove:
    data['records'][0]['fields'].pop(k, None)
    data['records'][0]['provenance'].pop(k, None)

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested lot fields.")
