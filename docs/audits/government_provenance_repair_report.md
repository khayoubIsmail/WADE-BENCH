# Government Provenance Repair Report

## Scope
- Gold JSON files processed: 20
- Page snapshots used: 20 from `government_pages.zip`
- Provenance fields checked: 2282

## Audit counts

| Stage | OK | WARN | FAIL |
|---|---:|---:|---:|
| Before repair | 2272 | 7 | 3 |
| After repair | 2279 | 3 | 0 |

## Repairs applied
- Re-anchored provenance to unique XPath-resolved DOM elements and generated matching absolute CSS selectors.
- Replaced broad row/card selectors with field-level element selectors where the value is present in `page.html`.
- Fixed URL fields to point to exact `href`, `src`, or `content` attributes where available.
- Cleared wrong/unverifiable URL provenance when the value was not present in the frozen static DOM.
- Removed invalid SAM CSS selectors with unescaped colon classes by generating safe absolute selectors.
- Fixed known normalization errors: Canada sentinel dates, TED DD/MM publication dates, Sell2Wales DD/MM closing dates, SAM GMT+1 sign, CFIN contract dates, and FAT/Gebiz published dates.

## After-repair status by task

| Task | OK | WARN | FAIL |
|---|---:|---:|---:|
| `WBV1_GOV_CANADA_001_LISTING` | 300 | 0 | 0 |
| `WBV1_GOV_CANADA_002_DETAIL` | 13 | 0 | 0 |
| `WBV1_GOV_CFIN_001_LISTING` | 200 | 0 | 0 |
| `WBV1_GOV_CFIN_002_DETAIL` | 22 | 0 | 0 |
| `WBV1_GOV_FAT_001_LISTING` | 80 | 0 | 0 |
| `WBV1_GOV_FAT_002_DETAIL` | 17 | 0 | 0 |
| `WBV1_GOV_GETS_001_LISTING` | 175 | 0 | 0 |
| `WBV1_GOV_GETS_002_DETAIL` | 16 | 0 | 0 |
| `WBV1_GOV_PUBLICCONTRACTSSCOTLAND_001_LISTING` | 80 | 0 | 0 |
| `WBV1_GOV_PUBLICCONTRACTSSCOTLAND_002_DETAIL` | 10 | 1 | 0 |
| `WBV1_GOV_SAM_001_LISTING` | 275 | 0 | 0 |
| `WBV1_GOV_SAM_002_DETAIL` | 13 | 2 | 0 |
| `WBV1_GOV_SELL2WALES_001_LISTING` | 120 | 0 | 0 |
| `WBV1_GOV_SELL2WALES_002_DETAIL` | 19 | 0 | 0 |
| `WBV1_GOV_TED_001_LISTING` | 496 | 0 | 0 |
| `WBV1_GOV_TED_002_DETAIL` | 28 | 0 | 0 |
| `WBV1_GOV_UNGM_001_LISTING` | 240 | 0 | 0 |
| `WBV1_GOV_UNGM_002_DETAIL` | 14 | 0 | 0 |
| `WBV1_GOV_WORLDBANK_PROCUREMENT_001_LISTING` | 140 | 0 | 0 |
| `WBV1_GOV_WORLDBANK_PROCUREMENT_002_DETAIL` | 21 | 0 | 0 |

## Residual non-OK reasons

| Reason | Count |
|---|---:|
| `explicitly_unverifiable_in_static_dom` | 3 |

## Residual non-OK examples

- `WBV1_GOV_PUBLICCONTRACTSSCOTLAND_002_DETAIL` / `WBV1_GOV_PUBLICCONTRACTSSCOTLAND_002_DETAIL_001` / `status`: **WARN** — explicitly_unverifiable_in_static_dom
- `WBV1_GOV_SAM_002_DETAIL` / `WBV1_GOV_SAM_002_DETAIL_001` / `buyer_name`: **WARN** — explicitly_unverifiable_in_static_dom
- `WBV1_GOV_SAM_002_DETAIL` / `WBV1_GOV_SAM_002_DETAIL_001` / `tender_url`: **WARN** — explicitly_unverifiable_in_static_dom

## Changed entries

- Total changed provenance/normalization entries: 2211
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_001` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_001` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_001` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_001` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_001` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_001` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_002` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_002` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_002` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_002` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_002` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_002` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_003` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_003` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_003` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_003` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_003` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_003` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_004` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_004` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_004` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_004` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_004` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_004` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_005` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_005` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_005` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_005` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_005` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_005` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_006` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_006` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_006` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_006` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_006` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_006` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_007` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_007` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_007` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_007` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_007` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_007` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_008` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_008` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_008` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_008` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_008` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_008` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_009` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_009` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_009` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_009` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_009` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_009` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_010` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_010` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_010` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_010` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_010` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_010` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_011` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_011` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_011` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_011` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_011` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_011` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_012` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_012` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_012` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_012` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_012` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_012` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_013` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_013` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_013` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_013` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_013` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_013` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_014` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_014` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_014` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_014` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_014` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_014` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_015` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_015` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_015` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_015` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_015` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_015` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_016` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_016` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_016` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_016` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_016` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_016` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_017` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_017` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_017` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_017` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_017` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_017` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_018` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_018` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_018` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_018` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_018` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_018` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_019` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_019` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_019` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_019` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_019` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_019` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_020` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_020` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_020` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_020` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_020` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_020` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_021` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_021` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_021` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_021` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_021` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_021` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_022` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_022` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_022` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_022` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_022` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_022` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_023` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_023` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_023` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_023` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_023` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_023` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_024` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_024` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_024` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_024` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_024` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_024` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_025` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_025` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_025` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_025` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_025` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_025` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_026` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_026` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_026` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_026` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_026` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_026` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_027` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_027` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_027` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_027` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_027` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_027` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_028` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_028` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_028` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_028` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_028` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_028` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_029` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_029` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_029` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_029` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_029` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_029` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_030` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_030` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_030` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_030` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_030` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_030` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_031` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_031` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_031` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_031` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_031` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_031` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_032` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_032` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_032` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_032` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_032` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_032` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_033` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_033` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_033` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_033` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_033` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_033` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_034` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_034` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_034` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_034` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_034` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_034` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_035` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_035` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_035` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_035` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_035` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_035` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_036` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_036` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_036` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_036` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_036` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_036` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_037` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_037` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_037` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_037` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_037` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_037` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_038` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_038` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_038` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_038` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_038` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_038` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_039` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_039` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_039` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_039` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_039` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_039` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_040` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_040` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_040` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_040` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_040` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_040` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_041` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_041` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_041` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_041` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_041` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_041` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_042` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_042` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_042` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_042` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_042` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_042` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_043` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_043` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_043` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_043` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_043` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_043` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_044` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_044` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_044` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_044` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_044` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_044` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_045` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_045` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_045` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_045` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_045` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_045` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_046` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_046` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_046` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_046` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_046` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_046` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_047` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_047` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_047` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_047` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_047` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_047` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_048` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_048` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_048` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_048` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_048` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_048` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_049` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_049` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_049` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_049` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_049` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_049` / `buyer`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_050` / `tender_title`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_050` / `tender_url`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_050` / `category`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_050` / `publication_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_050` / `closing_date`: reanchored exact XPath/CSS
- `WBV1_GOV_CANADA_001_LISTING` / `WBV1_GOV_CANADA_001_LISTING_050` / `buyer`: reanchored exact XPath/CSS
