import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

price_and_sales_history = [
  {
    "Date": "5/27/2026",
    "Details": "Listed",
    "Price": "$2,395,000",
    "Change": "6.44%",
    "Source": "MLS"
  },
  {
    "Date": "6/10/2021",
    "Details": "Sold",
    "Price": "$2,250,000",
    "Change": "—",
    "Source": "Public Record"
  }
]

tax_history = [
  {
    "Year": "2025",
    "Property_Taxes": "$29,569",
    "Tax_Change": "3%",
    "Tax_Assessment": "$2,435,470",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2024",
    "Property_Taxes": "$28,718",
    "Tax_Change": "2%",
    "Tax_Assessment": "$2,387,717",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2023",
    "Property_Taxes": "$28,293",
    "Tax_Change": "1300%",
    "Tax_Assessment": "$2,340,900",
    "Assessment_Change": "1978%"
  },
  {
    "Year": "2022",
    "Property_Taxes": "$2,021",
    "Tax_Change": "2%",
    "Tax_Assessment": "$112,676",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2021",
    "Property_Taxes": "$1,980",
    "Tax_Change": "-4%",
    "Tax_Assessment": "$110,468",
    "Assessment_Change": "1%"
  },
  {
    "Year": "2020",
    "Property_Taxes": "$2,061",
    "Tax_Change": "6%",
    "Tax_Assessment": "$109,338",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2019",
    "Property_Taxes": "$1,947",
    "Tax_Change": "3%",
    "Tax_Assessment": "$107,196",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2018",
    "Property_Taxes": "$1,883",
    "Tax_Change": "20%",
    "Tax_Assessment": "$105,096",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2017",
    "Property_Taxes": "$1,563",
    "Tax_Change": "4%",
    "Tax_Assessment": "$103,036",
    "Assessment_Change": "2%"
  },
  {
    "Year": "2016",
    "Property_Taxes": "$1,507",
    "Tax_Change": "5%",
    "Tax_Assessment": "$101,018",
    "Assessment_Change": "2%"
  }
]

new_fields = {
    "Price_&_Sales_History": {
        "value": "2 records",
        "normalized": price_and_sales_history
    },
    "Tax_History": {
        "value": "10 records",
        "normalized": tax_history
    }
}

new_provenance = {
    "Price_&_Sales_History": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "table",
        "xpath": "//table",
        "text_quote": "Price & Sales History"
    },
    "Tax_History": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "table",
        "xpath": "//table",
        "text_quote": "Tax History"
    }
}

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested history tables.")
