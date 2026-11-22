import json
import re

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_APARTMENTS_002_DETAIL\page.html'
try:
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    # Find all webp images from cbhomes.com
    images = list(dict.fromkeys(re.findall(r'https://m[0-9]*\.cbhomes\.com/[^\"\']+\.webp', html)))
except Exception as e:
    images = []

data_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_APARTMENTS_002_DETAIL.json'

with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

data['records'][0]['fields'] = {
    'address': {
        'value': '130 Maywood Dr San Francisco, CA 94127',
        'normalized': '130 Maywood Dr San Francisco, CA 94127'
    },
    'price': {
        'value': '$2,395,000',
        'normalized': 2395000
    },
    'sale_type': {
        'value': 'For Sale',
        'normalized': 'for_sale'
    },
    'status': {
        'value': 'Pending',
        'normalized': 'pending'
    },
    'property_type': {
        'value': 'Single Family',
        'normalized': 'single_family'
    },
    'bedrooms': {
        'value': '4 Beds',
        'normalized': 4
    },
    'bathrooms_full': {
        'value': '2 Full Baths',
        'normalized': 2
    },
    'bathrooms_half': {
        'value': '1 Partial Bath',
        'normalized': 1
    },
    'square_feet': {
        'value': '2,392 Sq. Ft.',
        'normalized': 2392
    },
    'garage_spaces': {
        'value': '2 Car Garage',
        'normalized': 2
    },
    'images_urls': {
        'value': images,
        'normalized': images
    }
}

data['records'][0]['provenance'] = {
    'address': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'h1#main-content',
        'xpath': "//h1[@id='main-content']",
        'text_quote': '130 Maywood Dr San Francisco, CA 94127'
    },
    'price': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': "p.price-block span[itemprop='price']",
        'xpath': "//p[contains(@class,'price-block')]//span[@itemprop='price']",
        'text_quote': '$2,395,000'
    },
    'sale_type': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': 'For Sale'
    },
    'status': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': 'Pending'
    },
    'property_type': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': 'Single Family'
    },
    'bedrooms': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': '4 Beds'
    },
    'bathrooms_full': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': '2 Full Baths'
    },
    'bathrooms_half': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': '1 Partial Bath'
    },
    'square_feet': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': '2,392 Sq. Ft.'
    },
    'garage_spaces': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': 'ul.details.action-bar-feature',
        'xpath': "//ul[contains(@class,'details') and contains(@class,'action-bar-feature')]",
        'text_quote': '2 Car Garage'
    },
    'images_urls': {
        'snapshot_id': 'coldwell_banker_130_maywood_dr_detail',
        'css_selector': '.owl-carousel img',
        'xpath': "//*[contains(@class,'owl-carousel')]//img",
        'text_quote': ''
    }
}

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Updated JSON with {len(images)} images.")
