import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_FINN_EIENDOM_001_LISTING\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_FINN_EIENDOM_001_LISTING.json'
SNAP_ID = "SNAP_REAL_FINN_EIENDOM_001_LISTING"

with open(html_path, encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

def get_xpath(element):
    if not element: return None
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        if parent.name == '[document]': break
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) == 1:
            components.append(child.name)
        else:
            try:
                index = siblings.index(child) + 1
                components.append(f"{child.name}[{index}]")
            except ValueError:
                components.append(child.name)
        child = parent
    components.reverse()
    return f"/{'/'.join(components)}"

def build_css(el):
    if not el: return ""
    # Check self first for stable attrs
    if el.get('id'): return f"{el.name}#{el['id']}"
    if el.get('data-testid'): return f"{el.name}[data-testid=\"{el['data-testid']}\"]"
    if el.get('data-tracking'): return f"{el.name}[data-tracking=\"{el['data-tracking']}\"]"
    if el.get('aria-label'): return f"{el.name}[aria-label=\"{el['aria-label']}\"]"
    # Walk up ancestors looking for a stable scoping class
    STABLE_CLASSES = {
        'whitespace-normal': 'span.whitespace-normal',
        'inline-block': 'span.inline-block',
        'sf-search-ad-link': 'a.sf-search-ad-link',
        'card': 'article.card',
        'object-center': 'img.object-center',
    }
    for cls, sel in STABLE_CLASSES.items():
        if el.name == sel.split('.')[0].split('[')[0] and cls in (el.get('class') or []):
            return sel
    # Scope with first stable parent class
    PARENT_SCOPE_MAP = [
        ('font-bold', 'div.font-bold > span'),
        ('s-text-subtle', 'div.s-text-subtle > span'),
    ]
    for parent_cls, scoped_sel in PARENT_SCOPE_MAP:
        if el.parent and parent_cls in (el.parent.get('class') or []):
            return scoped_sel
    # Location address: text-s + s-text-subtle (without whitespace-normal)
    classes = el.get('class') or []
    if el.name == 'span' and 'text-s' in classes and 's-text-subtle' in classes and 'whitespace-normal' not in classes:
        return 'span.text-s.s-text-subtle'
    # Fallback: use first non-generic class on self
    classes = el.get('class', [])
    stable = [c for c in classes if len(c) > 3 and not c.startswith('sc-') and c not in ('flex', 'col', 'row', 'grid', 'hidden', 'inline', 'block', 'relative', 'absolute', 'w-full', 'h-full', 'overflow-hidden')]
    if stable: return f"{el.name}.{stable[0]}"
    return el.name

def prov(el, val, snap_id=SNAP_ID):
    val_str = val if isinstance(val, str) else str(val)
    return {
        "snapshot_id": snap_id,
        "css_selector": build_css(el),
        "xpath": get_xpath(el),
        "text_quote": val_str[:80]
    }

def clean_price(text):
    """Convert Norwegian price format to integer: '5 850 000 kr' -> 5850000"""
    text = text.replace('\xa0', '').replace(' ', '')
    m = re.search(r'[\d]+', text)
    return int(re.sub(r'[^\d]', '', text)) if m else None

def parse_card(card, idx):
    fields = {}
    provenance = {}

    def add(key, val, el, norm=None):
        if val is None or val == '': return
        fields[key] = {"value": val, "normalized": norm if norm is not None else val}
        provenance[key] = prov(el, val)

    # listing_url - from first sf-search-ad-link
    link_el = card.find('a', class_='sf-search-ad-link')
    if link_el and link_el.get('href'):
        href = link_el['href']
        if href.startswith('/'):
            href = 'https://www.finn.no' + href
        add('listing_url', href, link_el)

    # listing_title - h2
    h2 = card.find('h2')
    if h2:
        add('listing_title', h2.text.strip(), h2)

    # agent_branding (agency name) - class 'whitespace-normal'
    agent_el = card.find('span', class_='whitespace-normal')
    if agent_el:
        add('agent_branding', agent_el.text.strip(), agent_el)

    # agent_branding_logo - logo img (alt='Megler logo' or '' with logo URL path)
    logo_img = card.find('img', alt='Megler logo') or card.find('img', alt='', src=lambda x: x and ('logo/cp' in x or 'mmo/logo' in x))
    if logo_img:
        add('agent_branding_logo', logo_img['src'], logo_img)

    # location/address - has 's-text-subtle' but NOT 'whitespace-normal' in class list
    loc_el = next(
        (s for s in card.find_all('span')
         if isinstance(s.get('class'), list)
         and 's-text-subtle' in s.get('class')
         and 'whitespace-normal' not in s.get('class')
         and s.text.strip()),
        None
    )
    if loc_el:
        add('location', loc_el.text.strip(), loc_el)

    # image_url - first img in carousel
    img_el = card.find('img', alt=lambda x: x and 'annonsen' in x)
    if img_el:
        src = img_el.get('src', '')
        add('image_url', src, img_el)

    # All leaf spans for structured data
    leaf_spans = [s for s in card.find_all('span') if s.text.strip() and not s.find('span') and 'sr-only' not in (s.get('class') or [])]

    # Find area (m²), price, property details
    for s in leaf_spans:
        txt = s.text.strip()
        # area e.g. "80 m²"
        if re.match(r'^\d+\s*m²$', txt):
            add('area', txt, s)
        # main price e.g. "5 850 000 kr"
        elif re.match(r'^[\d\s\xa0]+kr$', txt) and '\xa0' in txt:
            clean = txt.replace('\xa0', ' ')
            num = clean_price(txt)
            add('price', clean, s, num)
        # totalpris/fellesutg line — split into two fields
        elif 'Totalpris' in txt or 'Fellesutg' in txt:
            # total_price
            tp_match = re.search(r'Totalpris:\s*([\d\s\xa0,\-]+kr)', txt)
            if tp_match:
                tp_raw = tp_match.group(1).strip().replace('\xa0', ' ')
                tp_num_str = re.sub(r'[^\d]', '', tp_raw.split('-')[0])
                tp_num = int(tp_num_str) if tp_num_str else None
                add('total_price', tp_raw, s, tp_num)
            # monthly_fees (Fellesutgifter)
            fe_match = re.search(r'Fellesutg\.:\s*([\d\s\xa0]+kr)', txt)
            if fe_match:
                fe_raw = fe_match.group(1).strip().replace('\xa0', ' ')
                fe_num_str = re.sub(r'[^\d]', '', fe_raw)
                fe_num = int(fe_num_str) if fe_num_str else None
                add('monthly_fees', fe_raw, s, fe_num)
        # property type line e.g. "Selveier ∙ Leilighet ∙ 2 soverom"
        elif '∙' in txt and ('Leilighet' in txt or 'Enebolig' in txt or 'Tomannsbolig' in txt or 'Rekkehus' in txt or 'soverom' in txt):
            parts = [p.strip() for p in txt.split('∙')]
            # ownership
            if len(parts) >= 1: add('ownership_type', parts[0], s)
            # property_type
            if len(parts) >= 2: add('property_type', parts[1], s)
            # bedrooms
            if len(parts) >= 3:
                bed_match = re.search(r'(\d+)\s*soverom', parts[2])
                if bed_match:
                    add('bedrooms', parts[2].strip(), s, int(bed_match.group(1)))
        # Open house / Visning
        elif txt.startswith('Visning'):
            NO_MONTHS = {
                'januar': 'January', 'februar': 'February', 'mars': 'March',
                'april': 'April', 'mai': 'May', 'juni': 'June',
                'juli': 'July', 'august': 'August', 'september': 'September',
                'oktober': 'October', 'november': 'November', 'desember': 'December'
            }
            NO_DAYS = {
                0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                4: 'Friday', 5: 'Saturday', 6: 'Sunday'
            }
            import datetime
            m = re.search(r'(\d+)\.\s*(\w+)\s+kl\.\s*(\d{1,2}:\d{2})', txt)
            if m:
                day_num = int(m.group(1))
                month_no = m.group(2).lower()
                time_start = m.group(3)
                month_en = NO_MONTHS.get(month_no, month_no.capitalize())
                # Resolve weekday name from date (assume year 2026 based on snapshot)
                try:
                    month_idx = list(NO_MONTHS.keys()).index(month_no) + 1
                    dt = datetime.date(2026, month_idx, day_num)
                    weekday = NO_DAYS[dt.weekday()]
                except Exception:
                    weekday = None
                normalized = {
                    "day": weekday,
                    "date": f"{day_num} {month_en}",
                    "timing_start": time_start,
                    "time_end": None
                }
            else:
                # "Visning etter avtale" or other
                normalized = {
                    "day": None,
                    "date": None,
                    "timing_start": "by appointment",
                    "time_end": None
                }
            el_span = s
            prov_entry = prov(el_span, txt)
            fields['Open_House_time'] = {"value": txt, "normalized": normalized}
            provenance['Open_House_time'] = prov_entry

    return fields, provenance

cards = soup.find_all('article')
print(f"Found {len(cards)} listing cards")

records = []
for i, card in enumerate(cards):
    fields, provenance = parse_card(card, i)
    record_id = f"WBV1_REAL_FINN_EIENDOM_001_LISTING_{str(i+1).zfill(3)}"
    records.append({
        "gold_record_id": record_id,
        "fields": fields,
        "provenance": provenance
    })
    print(f"[{i+1}] {fields.get('listing_title', {}).get('value', 'N/A')[:60]} | price={fields.get('price', {}).get('value', 'N/A')}")

with open(json_path, 'r', encoding='utf-8') as f:
    out_data = json.load(f)

out_data['records'] = records
out_data['annotation_metadata']['total_records_extracted'] = len(records)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"\nDone. Wrote {len(records)} records.")
