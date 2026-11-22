# WADE-Bench v1 — E-commerce Domain Annotation Guidelines

## Scope
- 10 websites
- 20 tasks
- 2 schemas: `product_listing_v1`, `product_detail_v1`
- frozen snapshot evaluation
- structured JSON output with field-level provenance

## Final websites
IKEA US; H&M US; Sephora regional redirect; REI; Decathlon; Jumia Egypt; Allbirds; Glossier; Etsy; ASOS.

B&H Photo was rejected for v1 because it triggered Cloudflare human verification.

## Annotation workflow
1. Open the verified listing URL from `ecommerce_websites_final_10.csv`.
2. Save `page.html`, `screenshot.png`, and `metadata.json`.
3. Annotate listing records using `product_listing_v1`.
4. Open 1–2 sample detail pages from the listing page.
5. Save detail snapshots.
6. Annotate up to 10 detail records using `product_detail_v1`.

## Rules
- Do not invent missing values.
- Use `null` for missing optional fields.
- Preserve raw page text for prices, ratings, sizes, discounts, and delivery text.
- Add normalized values only when safely parseable.
- Every required field must include provenance: URL, snapshot_id, CSS selector or XPath, and text quote or attribute value.

## Record matching
Primary key: `product_url`.
Fallback key: `product_name + price_raw + image_url`.

## Caveats
- Sephora redirected from `sephora.com` to `sephora.de` in the verification environment.
- Etsy is intentionally noisy and useful as a harder marketplace case.
- ASOS replaces B&H Photo.
