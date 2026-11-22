import json
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
    html_path = r'data/raw_snapshots/jobs/postjobfree_listing/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_POSTJOBFREE_001_LISTING.json'
    snapshot_id = 'postjobfree_listing'

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    cards = soup.find_all('div', class_='snippetPadding')
    print(f'Found {len(cards)} job listings')

    records = []
    for i, c in enumerate(cards, start=1):
        record_id = f'WBV1_JOBS_POSTJOBFREE_001_LISTING_{i:03d}'

        # title & url
        title_el = c.find('h3', class_='itemTitle')
        a_el = title_el.find('a') if title_el else None
        title_val = a_el.get_text(strip=True) if a_el else None
        href = a_el.get('href') if a_el else None
        if href and href.startswith('/'):
            href = 'https://www.postjobfree.com' + href
        url_val = href

        # company
        company_el = c.find('span', class_='colorCompany')
        company_val = company_el.get_text(strip=True) if company_el else None

        # location
        location_el = c.find('span', class_='colorLocation')
        location_val = location_el.get_text(strip=True) if location_el else None

        # desc
        desc_el = c.find('span', class_='jdSnippet')
        desc_val = desc_el.get_text(strip=True) if desc_el else None

        # date
        date_el = c.find('span', class_='colorDate')
        date_val = date_el.get_text(strip=True) if date_el else None

        # salary
        salary_el = c.find('div', class_='colorSalary')
        salary_val = salary_el.get_text(strip=True) if salary_el else None

        fields = {
            'title': {'value': title_val, 'normalized': title_val},
            'url_job': {'value': url_val, 'normalized': url_val},
            'company': {'value': company_val, 'normalized': company_val},
            'location': {'value': location_val, 'normalized': location_val},
            'salary': {'value': salary_val, 'normalized': salary_val},
            'description': {'value': desc_val, 'normalized': desc_val},
            'date_publication': {'value': date_val, 'normalized': date_val},
        }

        # provenance
        provenance = {}
        el_map = {
            'title': a_el,
            'url_job': a_el,
            'company': company_el,
            'location': location_el,
            'salary': salary_el,
            'description': desc_el,
            'date_publication': date_el,
        }
        for field, el in el_map.items():
            val = fields[field]['value']
            if el and val is not None:
                quote = val[0] if isinstance(val, list) and val else str(val)
                quote = (quote[:100] + '...') if len(quote) > 100 else quote
                provenance[field] = {
                    'snapshot_id': snapshot_id,
                    'xpath': get_xpath(el),
                    'css_selector': get_css(el),
                    'text_quote': quote,
                }
            else:
                provenance[field] = {
                    'snapshot_id': snapshot_id,
                    'xpath': None,
                    'css_selector': None,
                    'text_quote': None,
                }

        records.append({
            'gold_record_id': record_id,
            'fields': fields,
            'provenance': provenance,
        })

    data = {
        'task_id': 'WBV1_JOBS_POSTJOBFREE_001_LISTING',
        'website_id': 'postjobfree',
        'schema_id': 'job_listing_v1',
        'snapshot_id': snapshot_id,
        'snapshot_path': 'raw_snapshots/jobs/postjobfree_listing',
        'live_url': 'https://www.postjobfree.com/jobs?q=engineer',
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
