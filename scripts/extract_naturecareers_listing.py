import json
import re
from bs4 import BeautifulSoup


def get_xpath(element):
    if element is None:
        return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]':
            break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            index = next((i for i, s in enumerate(siblings) if s is child), 0) + 1
            components.append(f'{child.name}[{index}]')
        child = parent
    components.reverse()
    return '/' + '/'.join(components)


def get_css(element):
    if element is None:
        return None
    if element.get('id'):
        return f"#{element.get('id')}"
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]':
            break
        if parent.get('id'):
            siblings = parent.find_all(child.name, recursive=False)
            if len(siblings) == 1:
                components.append(child.name)
            else:
                index = next((i for i, s in enumerate(siblings) if s is child), 0) + 1
                components.append(f'{child.name}:nth-of-type({index})')
            components.append(f"#{parent.get('id')}")
            break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            index = next((i for i, s in enumerate(siblings) if s is child), 0) + 1
            components.append(f'{child.name}:nth-of-type({index})')
        child = parent
    components.reverse()
    return ' > '.join(components)


def extract_listing():
    html_path = r'data/raw_snapshots/jobs/naturecareers_listing/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_NATURECAREERS_001_LISTING.json'
    snapshot_id = 'naturecareers_listing'

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    detail_divs = soup.find_all('div', class_='lister__details')
    print(f'Found {len(detail_divs)} job listings')

    records = []
    for i, d in enumerate(detail_divs, start=1):
        record_id = f'WBV1_JOBS_NATURECAREERS_001_LISTING_{i:03d}'

        # title
        title_el = d.find('h3', class_='lister__header')
        title_val = title_el.get_text(strip=True) if title_el else None

        # job_url
        a_el = d.find('a', class_='js-clickable-area-link')
        href = a_el['href'].strip() if a_el else None
        if href and href.startswith('/'):
            href = 'https://www.nature.com' + href
        job_url_val = href

        # logo (alt + src)
        img_el = d.find('img', class_='lister__logo')
        logo_alt = img_el.get('alt', '').replace(' logo', '').strip() if img_el else None
        logo_src = img_el.get('src', '').strip() if img_el else None
        if logo_src and logo_src.startswith('//'):
            logo_src = 'https:' + logo_src
        logo_val = logo_src  # normalized as full URL

        # items (meta list: location, salary, recruiter)
        items_val = [li.get_text(strip=True) for li in d.find_all('li', class_='lister__meta-item')]

        # description
        desc_el = d.find('p', class_='lister__description')
        desc_val = desc_el.get_text(strip=True) if desc_el else None

        fields = {
            'title': {'value': title_val, 'normalized': title_val},
            'logo': {'value': logo_val, 'normalized': logo_val},
            'job_url': {'value': job_url_val, 'normalized': job_url_val},
            'items': {'value': items_val if items_val else None, 'normalized': items_val if items_val else None},
            'description': {'value': desc_val, 'normalized': desc_val},
        }

        # provenance
        provenance = {}
        el_map = {
            'title': title_el,
            'logo': img_el,
            'job_url': a_el,
            'items': d.find('ul', class_='lister__meta'),
            'description': desc_el,
        }
        for field, el in el_map.items():
            if el and fields[field]['value'] is not None:
                val = fields[field]['value']
                quote = val[0] if isinstance(val, list) and val else str(val)
                quote = (quote[:100] + '...') if len(quote) > 100 else quote
                provenance[field] = {
                    'snapshot_id': snapshot_id,
                    'xpath': get_xpath(el),
                    'css_selector': get_css(el),
                    'text_quote': quote,
                }

        records.append({
            'gold_record_id': record_id,
            'fields': fields,
            'provenance': provenance,
        })

    data = {
        'task_id': 'WBV1_JOBS_NATURECAREERS_001_LISTING',
        'website_id': 'naturecareers',
        'schema_id': 'job_listing_v1',
        'snapshot_id': snapshot_id,
        'snapshot_path': 'raw_snapshots/jobs/naturecareers_listing',
        'live_url': 'https://www.nature.com/naturecareers/jobs',
        'annotation_metadata': {
            'annotation_version': 'v1',
            'annotator_id': 'ismail_khayoub',
            'verification_status': 'human_verified',
            'total_records_extracted': len(records),
        },
        'records': records,
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'Saved {len(records)} records to {json_path}')


if __name__ == '__main__':
    extract_listing()
