import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

gold_dir = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
files = sorted([f for f in os.listdir(gold_dir) if f.endswith('.json')])

results = {}
for fname in files:
    fpath = os.path.join(gold_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data.get('records', [])
    total_records = len(records)
    
    # field coverage
    all_field_names = set()
    for rec in records:
        all_field_names.update(rec.get('fields', {}).keys())
    
    # provenance coverage
    has_prov = sum(1 for rec in records if rec.get('provenance'))
    
    # check price normalization compliance
    NON_NUMERIC_PRICES = {'auction', 'negotiation', 'deadline sale', 'tender', 'price by negotiation', 'contact agent', 'ask agent'}
    price_norm_issues = 0
    for rec in records:
        fields = rec.get('fields', {})
        if 'price' in fields:
            norm = fields['price'].get('normalized')
            value = fields['price'].get('value', '')
            # skip if value is a non-numeric placeholder
            if isinstance(value, str) and value.lower().strip() in NON_NUMERIC_PRICES:
                continue
            if not isinstance(norm, dict):
                price_norm_issues += 1

    # check bed normalization compliance
    bed_norm_issues = 0
    BED_FIELDS = ['bedrooms', 'BEDROOMS', 'beedrooms']
    for rec in records:
        fields = rec.get('fields', {})
        for bf in BED_FIELDS:
            if bf in fields:
                norm = fields[bf].get('normalized')
                if norm is not None and not isinstance(norm, int):
                    bed_norm_issues += 1

    # check date normalization compliance (should be ISO like YYYY-MM-DD or YYYY-MM)
    import re
    date_norm_issues = 0
    DATE_FIELDS = ['published_date', 'published date', 'listed_datetime']
    for rec in records:
        fields = rec.get('fields', {})
        for df in DATE_FIELDS:
            if df in fields:
                norm = fields[df].get('normalized')
                if norm and isinstance(norm, str):
                    if not re.match(r'^\d{4}', norm):
                        date_norm_issues += 1

    # field name issues (non snake_case, not canonical)
    NON_CANONICAL = ['beedrooms', 'location', 'listed_by', 'listed by', 'published date', 'Furnish type', 'Key features']
    field_name_issues = [f for f in all_field_names if f in NON_CANONICAL or (not f.islower() and not f.isupper())]
    
    results[fname] = {
        'total_records': total_records,
        'fields': sorted(all_field_names),
        'provenance_coverage': "%d/%d" % (has_prov, total_records),
        'schema_id': data.get('schema_id', '?'),
        'annotation_status': data.get('annotation_metadata', {}).get('verification_status', '?'),
        'price_norm_issues': price_norm_issues,
        'bed_norm_issues': bed_norm_issues,
        'date_norm_issues': date_norm_issues,
        'field_name_issues': field_name_issues,
    }

for fname, r in results.items():
    tr = r['total_records']
    pni = r['price_norm_issues']
    bni = r['bed_norm_issues']
    dni = r['date_norm_issues']
    fni = r['field_name_issues']
    prov = r['provenance_coverage']
    schema = r['schema_id']
    status = r['annotation_status']
    fields = r['fields']
    print("--- %s ---" % fname)
    print("  Records: %d" % tr)
    print("  Schema: %s" % schema)
    print("  Status: %s" % status)
    print("  Provenance: %s" % prov)
    print("  Price norm issues: %d" % pni)
    print("  Bed norm issues: %d" % bni)
    print("  Date norm issues: %d" % dni)
    print("  Field name issues: %s" % fni)
    print("  Fields (%d): %s" % (len(fields), fields))
    print()
