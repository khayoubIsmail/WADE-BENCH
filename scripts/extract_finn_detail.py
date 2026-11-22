import json
import re
from bs4 import BeautifulSoup

html_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate\SNAP_REAL_FINN_EIENDOM_002_DETAIL\page.html'
json_path = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate\WBV1_REAL_FINN_EIENDOM_002_DETAIL.json'
SNAP_ID = "SNAP_REAL_FINN_EIENDOM_002_DETAIL"

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
    if el.get('id'): return f"{el.name}#{el['id']}"
    if el.get('data-testid'): return f"{el.name}[data-testid=\"{el['data-testid']}\"]"
    if el.get('data-tracking'): return f"{el.name}[data-tracking=\"{el['data-tracking']}\"]"
    if el.get('aria-label'): return f"{el.name}[aria-label=\"{el['aria-label']}\"]"
    if el.get('aria-labelledby'): return f"{el.name}[aria-labelledby=\"{el['aria-labelledby']}\"]"
    if el.get('rel'): return f"{el.name}[rel=\"{' '.join(el['rel'])}\"]"
    # Scope via parent data-testid (e.g. dd inside div[data-testid="pricing-total-price"])
    parent = el.parent
    if parent and parent.get('data-testid'):
        return f"div[data-testid=\"{parent['data-testid']}\"] > {el.name}"
    # td: scope via table row
    if el.name == 'td' and parent and parent.name == 'tr':
        th = parent.find('th')
        if th:
            label = th.text.strip().replace('"', "'")
            return f"tr:has(th) > td"
    classes = el.get('class', [])
    stable = [c for c in classes if len(c) > 3 and not c.startswith('sc-') and c not in ('flex','col','row','grid','hidden','inline','block','relative','absolute','w-full','h-full')]
    if stable: return f"{el.name}.{stable[0]}"
    return el.name


def prov(el, val):
    val_str = val if isinstance(val, str) else str(val)
    return {
        "snapshot_id": SNAP_ID,
        "css_selector": build_css(el),
        "xpath": get_xpath(el),
        "text_quote": val_str[:80]
    }

def clean_kr(text):
    n = re.sub(r'[^\d]', '', text)
    return int(n) if n else None

fields = {}
provenance = {}

def add(key, val, el, norm=None):
    if val is None or (isinstance(val, str) and not val.strip()): return
    val_s = val.strip() if isinstance(val, str) else val
    fields[key] = {"value": val_s, "normalized": norm if norm is not None else val_s}
    provenance[key] = prov(el, val_s if isinstance(val_s, str) else str(val_s))

def testid(tid):
    return soup.find(attrs={'data-testid': tid})

# --- Core ---
h1 = soup.find('h1')
if h1:
    add('listing_title', h1.text.strip(), h1)

listing_url = "https://www.finn.no/realestate/homes/ad.html?finnkode=465141868"
canonical = soup.find('link', rel='canonical')
if canonical and canonical.get('href'):
    listing_url = canonical['href']
# Use canonical <link> el for provenance, fallback to first matching <a>
canonical_el = soup.find('link', rel='canonical') or soup.find('a', href=lambda x: x and 'finn.no/realestate' in x and 'finnkode' in x)
add('listing_url', listing_url, canonical_el or h1)

addr_el = testid('object-address')
if addr_el:
    add('location', addr_el.text.strip(), addr_el)

# Short description (subtitle block under h1, often a <p> near object-title)
obj_title = testid('object-title')
if obj_title:
    subtitle = obj_title.find('p') or obj_title.find('span', class_=lambda x: x and 'subtitle' in ' '.join(x or []))
    if not subtitle:
        # Try the area-description
        area_desc = testid('area-description')
        if area_desc: add('short_description', area_desc.text.strip(), area_desc)
    else:
        add('short_description', subtitle.text.strip(), subtitle)

# --- Images: lazy-loaded via data-srcset / srcset, each img has id="image-N" ---
gallery = testid('image-gallery') or testid('gallery-main')
if gallery:
    imgs_urls = []
    for img in gallery.find_all('img', alt='Galleribilde'):
        # Prefer srcset (already loaded) over data-srcset (lazy)
        srcset = img.get('srcset') or img.get('data-srcset') or ''
        if srcset:
            # Pick highest resolution: first entry is largest
            best = srcset.split(',')[0].strip().split(' ')[0]
            if best: imgs_urls.append(best)
        elif img.get('src'):
            imgs_urls.append(img['src'])
    if imgs_urls:
        add('images_urls', imgs_urls, gallery, imgs_urls)

# --- Pricing ---
price_el = testid('pricing-incicative-price') or soup.find(attrs={'data-testid': lambda x: x and 'indicative' in str(x).lower()})
# fallback: find the large bold price span
price_val_el = soup.find('span', class_=lambda x: x and 'text-28' in (x if isinstance(x, list) else x.split()))
if price_val_el:
    add('Price_Assessment', price_val_el.text.strip().replace('\xa0', ' '),
        price_val_el, clean_kr(price_val_el.text))

for field_key, testid_key in [
    ('Total_price',         'pricing-total-price'),
    ('costs',               'pricing-registration-charge'),
    ('Joint_debt',          'pricing-joint-debt'),
    ('Common_cost_mn',      'pricing-common-monthly-cost'),
    ('Joint_wealth',        'pricing-collective-assets'),
]:
    el = testid(testid_key)
    if el:
        dd = el.find('dd')
        if dd:
            raw = dd.text.strip().replace('\xa0', ' ')
            add(field_key, raw, dd, clean_kr(raw))

# --- Key Info ---
for field_key, testid_key, norm_fn in [
    ('Housing_type',          'info-property-type',     None),
    ('Internal_use_area',     'info-usable-i-area',     None),
    ('Use_Area',              'info-usable-area',       None),
    ('Year_of_construction',  'info-construction-year', lambda x: int(re.sub(r'[^\d]', '', x)) if re.search(r'\d{4}', x) else x),
    ('Land_area',             'info-plot-area',         None),
    ('Bedroom',               'info-bedrooms',          lambda x: int(re.sub(r'[^\d]', '', x)) if re.sub(r'[^\d]', '', x) else 0),
    ('Etage',                 'info-floor',             lambda x: int(re.sub(r'[^\d]', '', x)) if re.sub(r'[^\d]', '', x) else None),
    ('Room',                  'info-rooms',             lambda x: int(re.sub(r'[^\d]', '', x)) if re.sub(r'[^\d]', '', x) else None),
]:
    el = testid(testid_key)
    if el:
        # value is usually in the <dd> element
        dd = el.find('dd')
        val_el = dd if dd else el
        # strip the label (dt text)
        dt = el.find('dt')
        txt = val_el.text.strip()
        if dt and txt.startswith(dt.text.strip()):
            txt = txt[len(dt.text.strip()):].strip()
        add(field_key, txt, val_el, norm_fn(txt) if norm_fn else txt)

# Energy label from SVG aria-label
energy_section = testid('energy-label')
if energy_section:
    svg = energy_section.find('svg', attrs={'aria-label': True})
    if svg:
        label = svg['aria-label'].replace('Energimerke ', '')
        add('ATG_energy_Marking', svg['aria-label'], svg, label)

# --- About the home ---
about_el = testid('about-property')
if about_el:
    # Find text content, skipping any headings
    for h in about_el.find_all(['h2', 'h3']):
        h.decompose()
    about_text = about_el.get_text(separator=' ', strip=True)
    if about_text:
        add('About_the_home', about_text, about_el)

# --- Ad info: FINN code, published, reference ---
obj_info = testid('object-info')
if obj_info:
    for row in obj_info.find_all('tr'):
        th = row.find('th')
        td = row.find('td')
        if not th or not td: continue
        label = th.text.strip()
        value = td.text.strip()
        if 'Sist endret' in label or 'endret' in label:
            import datetime
            NO_MONTHS = {
                'januar':1,'februar':2,'mars':3,'april':4,'mai':5,'juni':6,
                'juli':7,'august':8,'september':9,'oktober':10,'november':11,'desember':12
            }
            import re as _re
            m = _re.search(r'(\d+)\.\s*(\w+)\s+(\d{4})\s+(\d{2}:\d{2})', value)
            if m:
                day_n, month_s, year_n, time_s = int(m.group(1)), m.group(2).lower(), int(m.group(3)), m.group(4)
                month_n = NO_MONTHS.get(month_s, 1)
                iso = f"{year_n:04d}-{month_n:02d}-{day_n:02d}T{time_s}:00"
            else:
                iso = value
            add('published_day', value, td, iso)
        elif 'Referanse' in label:
            add('Reference', value, td)

print("Fields extracted:", list(fields.keys()))

with open(json_path, 'r', encoding='utf-8') as f:
    out = json.load(f)

out['records'] = [{
    "gold_record_id": "WBV1_REAL_FINN_EIENDOM_002_DETAIL_001",
    "fields": fields,
    "provenance": provenance
}]
out['annotation_metadata']['total_records_extracted'] = 1

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("Done.")
