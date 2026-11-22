import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open(r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_MAROC_ANNONCES_002_DETAIL.json', encoding='utf-8'))
for k, v in data['records'][0]['fields'].items():
    print(f"{k}: {v['normalized']}")
