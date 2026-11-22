import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

schools_data = [
  {
    "name": "Miraloma Elementary School",
    "address": "175 Omar Way, San Francisco, CA 94127",
    "grades": "K-5",
    "distance": "0.8 mi"
  },
  {
    "name": "Denman (James) Middle School",
    "address": "241 Oneida Avenue, San Francisco, CA 94112",
    "grades": "6-8",
    "distance": "1.4 mi"
  },
  {
    "name": "S.F. International High School",
    "address": "655 De Haro Street, San Francisco, CA 94107",
    "grades": "9-12",
    "distance": "3.9 mi"
  },
  {
    "name": "Academy (The)- SF @Mcateer",
    "address": "555 Portola Drive, San Francisco, CA 94131",
    "grades": "9-12",
    "distance": "1.1 mi"
  },
  {
    "name": "Asawa (Ruth) San Francisco School Of The Arts, A Public School.",
    "address": "555 Portola Drive, San Francisco, CA 94131",
    "grades": "9-12",
    "distance": "1.1 mi"
  },
  {
    "name": "Lowell High School",
    "address": "1101 Eucalyptus Drive, San Francisco, CA 94132",
    "grades": "9-12",
    "distance": "1.2 mi"
  },
  {
    "name": "Lincoln (Abraham) High School",
    "address": "2162 24th Avenue, San Francisco, CA 94116",
    "grades": "9-12",
    "distance": "1.4 mi"
  },
  {
    "name": "Balboa High School",
    "address": "1000 Cayuga Avenue, San Francisco, CA 94112",
    "grades": "9-12",
    "distance": "1.5 mi"
  },
  {
    "name": "Jordan (June) School For Equity",
    "address": "325 La Grande Avenue, San Francisco, CA 94112",
    "grades": "9-12",
    "distance": "2.3 mi"
  }
]

new_fields = {
    "School_District": {
        "value": "San Francisco Unified School District",
        "normalized": "San Francisco Unified School District"
    },
    "Schools": {
        "value": [s["name"] for s in schools_data],
        "normalized": schools_data
    }
}

new_provenance = {
    "School_District": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "table",
        "xpath": "//table",
        "text_quote": "San Francisco Unified School District"
    },
    "Schools": {
        "snapshot_id": "coldwell_banker_130_maywood_dr_detail",
        "css_selector": "table",
        "xpath": "//table",
        "text_quote": "Miraloma Elementary School"
    }
}

data['records'][0]['fields'].update(new_fields)
data['records'][0]['provenance'].update(new_provenance)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated JSON with the requested school fields.")
