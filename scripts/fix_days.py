import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_CENTURY_21_001_LISTING.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

day_map = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday",
    "Sat": "Saturday",
    "Sun": "Sunday"
}

for record in data['records']:
    fields = record['fields']
    
    if 'Open_House_time' in fields:
        normalized = fields['Open_House_time'].get('normalized')
        if isinstance(normalized, dict) and 'day' in normalized:
            short_day = normalized['day']
            if short_day in day_map:
                normalized['day'] = day_map[short_day]

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Expanded short days to full days.")
