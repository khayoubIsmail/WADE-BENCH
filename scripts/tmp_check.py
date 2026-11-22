import json, glob, os

# Check all gold files across all domains for field completeness
domains = ['jobs', 'ecommerce', 'academic', 'government']
for domain in domains:
    files = sorted(glob.glob(f'data/gold/by_task/{domain}/*.json'))
    if not files:
        continue
    print(f"\n=== {domain.upper()} ===")
    for f in files:
        data = json.load(open(f, encoding='utf-8'))
        records = data.get('records', [])
        has_prov = any('provenance' in r for r in records)
        # Sample first record fields
        fields = {}
        if records:
            fields = records[0].get('fields', {})
        n = len(records)
        fname = os.path.basename(f)
        null_fields = [k for k, v in fields.items() if isinstance(v, dict) and v.get('value') is None]
        prov_str = "PROV" if has_prov else "NO-PROV"
        null_str = f"null:[{','.join(null_fields)}]" if null_fields else "all-filled"
        print(f"  {prov_str:7} | {n:3} rec | {null_str:40} | {fname}")
