import json
from datetime import datetime

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_002_DETAIL.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

for record in data['records']:
    if 'published_or_posted' in record.get('fields', {}):
        val = record['fields']['published_or_posted']['value']
        # e.g., "May 28, 2026 at 07:18 PM"
        try:
            dt = datetime.strptime(val, "%B %d, %Y at %I:%M %p")
            # Format to "05-28-2026 07:18 PM"
            formatted = dt.strftime("%m-%d-%Y %I:%M %p")
            record['fields']['published_or_posted']['normalized'] = formatted
        except Exception as e:
            print(f"Error parsing date: {e}")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Formatted published_or_posted date.")
