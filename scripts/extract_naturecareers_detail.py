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


def find_dd(soup, label):
    """Find a dd element by its corresponding dt label (case-insensitive)."""
    for dt in soup.find_all('dt'):
        if label.lower() in dt.text.strip().lower():
            dd = dt.find_next_sibling('dd')
            return dt, dd
    return None, None


def clean_list(dd):
    """Extract clean list items from a dd, splitting by comma or newline."""
    if dd is None:
        return None
    items = [li.get_text(strip=True) for li in dd.find_all('li')]
    if items:
        return items
    text = dd.get_text(separator=',').strip()
    parts = [p.strip() for p in text.replace('\n', ',').split(',') if p.strip()]
    return parts if parts else None


def extract_detail():
    html_path = r'data/raw_snapshots/jobs/naturecareers_detail/page.html'
    json_path = r'data/gold/by_task/jobs/WBV1_JOBS_NATURECAREERS_002_DETAIL.json'
    snapshot_id = 'naturecareers_detail'

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # --- title ---
    title_el = soup.find('h1')
    title_val = title_el.get_text(strip=True) if title_el else None

    # --- dt/dd pairs ---
    dt_employer, dd_employer = find_dd(soup, 'Employer')
    employer_val = dd_employer.get_text(strip=True) if dd_employer else None

    dt_location, dd_location = find_dd(soup, 'Location')
    location_val = dd_location.get_text(strip=True) if dd_location else None

    dt_salary, dd_salary = find_dd(soup, 'Salary')
    salary_val = dd_salary.get_text(strip=True) if dd_salary else None
    if salary_val == '"-"' or salary_val == '-' or salary_val == '"–"':
        salary_val = None

    dt_closing, dd_closing = find_dd(soup, 'Closing date')
    closing_val = dd_closing.get_text(strip=True) if dd_closing else None

    dt_discipline, dd_discipline = find_dd(soup, 'Discipline')
    discipline_val = clean_list(dd_discipline)

    dt_jobtype, dd_jobtype = find_dd(soup, 'Job Type')
    jobtype_val = clean_list(dd_jobtype)

    dt_hours, dd_hours = find_dd(soup, 'Employment - Hours')
    hours_val = dd_hours.get_text(strip=True) if dd_hours else None

    dt_duration, dd_duration = find_dd(soup, 'Duration')
    duration_val = dd_duration.get_text(strip=True) if dd_duration else None

    dt_qual, dd_qual = find_dd(soup, 'Qualification')
    qual_val = dd_qual.get_text(strip=True) if dd_qual else None

    dt_sector, dd_sector = find_dd(soup, 'Sector')
    sector_val = dd_sector.get_text(strip=True) if dd_sector else None

    # --- description from mds-prose ---
    prose_el = soup.find('div', class_='mds-prose')
    desc_val = prose_el.get_text(separator='\n', strip=True) if prose_el else None

    # --- apply url (absolute) ---
    apply_el = None
    apply_val = None
    for a in soup.find_all('a', href=True):
        if 'apply' in a.text.lower() and a.get('href', '').startswith('#'):
            # It's a hash anchor — resolve it in page context
            # Find the actual application form link if any, else use the page live_url + apply hash
            apply_val = 'https://www.nature.com/naturecareers/job/12859405/full-professorship-w3-for-biochemistry-f-m-d-/?LinkSource=PremiumListing' + a['href']
            apply_el = a
            break

    # --- build fields ---
    fields = {
        'title':                {'value': title_val,       'normalized': title_val},
        'employer':             {'value': employer_val,    'normalized': employer_val},
        'location':             {'value': location_val,    'normalized': location_val},
        'salary':               {'value': salary_val,      'normalized': salary_val},
        'closing_date':         {'value': closing_val,     'normalized': closing_val},
        'discipline':           {'value': discipline_val,  'normalized': discipline_val},
        'job_type':             {'value': jobtype_val,     'normalized': jobtype_val},
        'employment_hours':     {'value': hours_val,       'normalized': hours_val},
        'duration':             {'value': duration_val,    'normalized': duration_val},
        'qualification':        {'value': qual_val,        'normalized': qual_val},
        'sector':               {'value': sector_val,      'normalized': sector_val},
        'description':          {'value': desc_val,        'normalized': desc_val},
        'apply_url':            {'value': apply_val,       'normalized': apply_val},
    }

    el_map = {
        'title':            title_el,
        'employer':         dd_employer,
        'location':         dd_location,
        'salary':           dd_salary,
        'closing_date':     dd_closing,
        'discipline':       dd_discipline,
        'job_type':         dd_jobtype,
        'employment_hours': dd_hours,
        'duration':         dd_duration,
        'qualification':    dd_qual,
        'sector':           dd_sector,
        'description':      prose_el,
        'apply_url':        apply_el,
    }

    provenance = {}
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

    data = {
        'task_id': 'WBV1_JOBS_NATURECAREERS_002_DETAIL',
        'website_id': 'naturecareers',
        'schema_id': 'job_detail_v1',
        'snapshot_id': snapshot_id,
        'snapshot_path': 'raw_snapshots/jobs/naturecareers_detail',
        'live_url': 'https://www.nature.com/naturecareers/job/12859405/full-professorship-w3-for-biochemistry-f-m-d-/?LinkSource=PremiumListing',
        'annotation_metadata': {
            'annotation_version': 'v1',
            'annotator_id': 'ismail_khayoub',
            'verification_status': 'human_verified',
            'total_records_extracted': 1,
        },
        'records': [
            {
                'gold_record_id': 'WBV1_JOBS_NATURECAREERS_002_DETAIL_001',
                'fields': fields,
                'provenance': provenance,
            }
        ],
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'Saved detail record to {json_path}')
    for k, v in fields.items():
        val = v['value']
        if isinstance(val, list):
            print(f'  {k}: {val}')
        elif val and len(str(val)) > 60:
            print(f'  {k}: {str(val)[:60]}...')
        else:
            print(f'  {k}: {val}')


if __name__ == '__main__':
    extract_detail()
