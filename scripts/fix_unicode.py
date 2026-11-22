import json

json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_DAFT.IE_001_LISTING.json'

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

# Re-dump with ensure_ascii=False to ensure literal '€' characters instead of '\u20ac' escapes
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Rewrote JSON with literal unicode characters.")
