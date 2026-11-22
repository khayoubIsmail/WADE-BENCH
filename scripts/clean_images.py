import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'
with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

urls = data['records'][0]['fields']['images_urls']['value']

# 1. Clean up srcset artifacts
clean_urls = []
for u in urls:
    for sub_u in u.split(','):
        cleaned = sub_u.strip().split(' ')[0]
        if cleaned.endswith('.webp'):
            clean_urls.append(cleaned)

# 2. Keep only one per image ID
# Format is typically: https://m.cbhomes.com/p/1111/426131611/<IMAGE_ID>/<type>.webp
seen_ids = set()
unique_urls = []
for u in clean_urls:
    parts = u.split('/')
    if len(parts) >= 2:
        img_id = parts[-2]
        if img_id not in seen_ids:
            seen_ids.add(img_id)
            unique_urls.append(u)

data['records'][0]['fields']['images_urls']['value'] = unique_urls
data['records'][0]['fields']['images_urls']['normalized'] = unique_urls

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Filtered down to {len(unique_urls)} unique images.")
