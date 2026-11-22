import json

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

fields = data['records'][0]['fields']
provenance = data['records'][0]['provenance']

def get_new_key(old_key):
    if old_key == 'FencingDescription':
        return 'Fencing_Description'
    return old_key.replace(' ', '_')

new_fields = {}
for old_key, val in fields.items():
    new_fields[get_new_key(old_key)] = val

new_provenance = {}
for old_key, val in provenance.items():
    new_provenance[get_new_key(old_key)] = val

data['records'][0]['fields'] = new_fields
data['records'][0]['provenance'] = new_provenance

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Successfully renamed all keys to use underscores.")
