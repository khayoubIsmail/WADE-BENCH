import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

# The user wants specific keys added:
new_fields = {
    "Price": {
        "value": "$2,395,000",
        "normalized": 2395000
    },
    "HOA FEE": {
        "value": "$2/month",
        "normalized": {"amount": 2, "currency": "USD", "period": "month"}
    },
    "HOA FEE FREQ.": {
        "value": "Annually",
        "normalized": "annually"
    },
    "Status": {
        "value": "Pending",
        "normalized": "pending"
    },
    "Type": {
        "value": "Single Family",
        "normalized": "single_family"
    },
    "Source": {
        "value": "San_Francisco",
        "normalized": "San_Francisco"
    },
    "MLS ID": {
        "value": "426131611",
        "normalized": "426131611"
    },
    "Updated": {
        "value": "6/5/2026",
        "normalized": "2026-06-05"
    },
    "Added to Site": {
        "value": "15 day(s) ago",
        "normalized": "15_days_ago"
    }
}

new_provenance = {
    "Price": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "p.price-block span[itemprop='price']",
        "xpath": "//p[contains(@class,'price-block')]//span[@itemprop='price']",
        "text_quote": "$2,395,000"
    },
    "HOA FEE": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "$2/month"
    },
    "HOA FEE FREQ.": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "Annually"
    },
    "Status": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "p.price-block .property-status-indicator-text",
        "xpath": "//p[contains(@class,'price-block')]//*[contains(@class,'property-status-indicator-text')]",
        "text_quote": "Sale Pending"
    },
    "Type": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "ul.details.action-bar-feature",
        "xpath": "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        "text_quote": "Single Family"
    },
    "Source": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "San_Francisco"
    },
    "MLS ID": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "426131611"
    },
    "Updated": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "6/5/2026"
    },
    "Added to Site": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "#full-property-detail-body",
        "xpath": "//*[@id='full-property-detail-body']",
        "text_quote": "15 day(s) ago"
    }
}

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested General fields.")
