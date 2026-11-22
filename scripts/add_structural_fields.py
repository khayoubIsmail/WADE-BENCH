import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

new_fields = {
    "Architectural Style": {
        "value": "French, Traditional",
        "normalized": ["French", "Traditional"]
    },
    "Basement Desc.": {
        "value": "Partial",
        "normalized": "Partial"
    },
    "Foundation": {
        "value": "Concrete Perimeter",
        "normalized": "Concrete Perimeter"
    },
    "Roof": {
        "value": "Composition, Shingle",
        "normalized": ["Composition", "Shingle"]
    },
    "Windows": {
        "value": "Dual Pane Partial",
        "normalized": "Dual Pane Partial"
    },
    "Square Feet": {
        "value": "2,392",
        "normalized": 2392
    },
    "Sq. Ft. Source": {
        "value": "Graphic Artist",
        "normalized": "Graphic Artist"
    },
    "Living Area": {
        "value": "2,392 Sq. Ft.",
        "normalized": 2392
    },
    "Current Bldg. Use": {
        "value": "Residential",
        "normalized": "Residential"
    },
    "Year Built": {
        "value": "1937",
        "normalized": 1937
    }
}

new_provenance = {
    "Architectural Style": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "French, Traditional"
    },
    "Basement Desc.": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Partial"
    },
    "Foundation": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Concrete Perimeter"
    },
    "Roof": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Composition, Shingle"
    },
    "Windows": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Dual Pane Partial"
    },
    "Square Feet": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "2,392"
    },
    "Sq. Ft. Source": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Graphic Artist"
    },
    "Living Area": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "2,392 Sq. Ft."
    },
    "Current Bldg. Use": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Residential"
    },
    "Year Built": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "1937"
    }
}

keys_to_remove = ["square_feet", "year_built"]
for k in keys_to_remove:
    data['records'][0]['fields'].pop(k, None)
    data['records'][0]['provenance'].pop(k, None)

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested structural fields.")
