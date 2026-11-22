# Real Estate Domain — Gold Ground Truth Analysis
## Based on WADE_Bench_Annotation_Guidelines.md

---

## Overview

| Stat | Value |
|------|-------|
| Platforms | 10 |
| Task types | 2 (LISTING search, DETAIL page) |
| Gold JSON files | 20 |
| Total raw snapshots | 20 |
| Total extracted records | **570** |

### Platform Record Count

| File | Records | Schema |
|------|---------|--------|
| CENTURY_21_001_LISTING | **300** | real_estate_listing_v1 |
| FINN_EIENDOM_001_LISTING | 51 | real_estate_listing_v1 |
| REDFIN_001_LISTING | 41 | real_estate_listing_v1 |
| LEBONCOIN_001_LISTING | 35 | real_estate_listing_v1 |
| ONTHEMARKET_001_LISTING | 30 | real_estate_listing_v1 |
| RIGHTMOVE_001_LISTING | 25 | real_estate_listing_v1 |
| APARTMENTS_001_LISTING | 24 | real_estate_listing_v1 |
| MAROC_ANNONCES_001_LISTING | 20 | real_estate_listing_v1 |
| DAFT.IE_001_LISTING | 20 | real_estate_listing_v1 |
| REALESTATE.CO.NZ_001_LISTING | 14 | real_estate_listing_v1 |
| *(10 × DETAIL pages)* | 10 × 1 = **10** | real_estate_listing_v1 |
| **TOTAL** | **570** | |

---

## ✅ Provenance Coverage

**All 20 gold files have 100% provenance coverage** — every record has a `provenance` block with `snapshot_id`, `css_selector`, `xpath`, and `text_quote`.

> [!NOTE]
> However, provenance selectors across files use mostly **absolute** path selectors (long `nth-of-type` chains) rather than stable semantic selectors (e.g., `[data-testid='price']`). The guideline recommends stable selectors as primary and absolute as backup only.

---

## ⚠️ Issue 1 — Price Normalization (§1.2)

The guideline requires `price.normalized` to be a **structured object**:
```json
"price": {
  "value": "£475,000",
  "normalized": { "amount": 475000.0, "currency": { "name": "...", "code": "GBP", "symbol": "£" } }
}
```

**Status by file:**

| File | Price norm issues | Current format |
|------|-------------------|----------------|
| APARTMENTS_001_LISTING | ✅ 0 | correct dict |
| FINN_EIENDOM_001_LISTING | ❌ 48/51 records | string `"kr 3 290 000"` |
| LEBONCOIN_001_LISTING | ❌ 35/35 records | string `"395 000 €"` |
| LEBONCOIN_002_DETAIL | ✅ 0 | correct |
| MAROC_ANNONCES_001_LISTING | ❌ 19/20 records | string |
| MAROC_ANNONCES_002_DETAIL | ❌ 1/1 | string |
| ONTHEMARKET_001_LISTING | ❌ 28/30 records | string |
| ONTHEMARKET_002_DETAIL | ❌ 1/1 | string |
| REALESTATE.CO.NZ_001_LISTING | ❌ 14/14 records | string |
| REALESTATE.CO.NZ_002_DETAIL | ❌ 1/1 | string |
| REDFIN_001_LISTING | ❌ 41/41 records | string |
| REDFIN_002_DETAIL | ❌ 1/1 | string |
| RIGHTMOVE_001_LISTING | ❌ 25/25 records | string `"£200,000"` |
| RIGHTMOVE_002_DETAIL | ❌ 1/1 | string |

> [!CAUTION]
> This is the **most widespread issue** — affecting ~80% of all files. Price normalization must be updated to structured dicts with `amount` (float), `currency.name`, `currency.code`, and `currency.symbol`.

---

## ⚠️ Issue 2 — Field Name Canonicalization (§2)

The guideline mandates `snake_case` canonical field names.

### Non-canonical names found across files

| Field used | File(s) | Canonical name per guideline |
|---|---|---|
| `beedrooms` (typo) | RIGHTMOVE_001_LISTING | `bedrooms` |
| `Furnish type` (mixed case) | RIGHTMOVE_002_DETAIL | `furnish_type` |
| `Key features` (mixed case) | RIGHTMOVE_002_DETAIL | `key_features` |
| `Description` (capitalized) | RIGHTMOVE_002_DETAIL | `description` |
| `BEDROOMS` / `BATHROOMS` (uppercase) | RIGHTMOVE_002_DETAIL | `bedrooms` / `bathrooms` |
| `PROPERTY TYPE` | RIGHTMOVE_002_DETAIL | `property_type` |
| `published date` (space) | RIGHTMOVE_002_DETAIL | `published_date` |
| `location` | All files | `address` per guideline §2 |
| `listed_by` | REDFIN, RIGHTMOVE | `listing_agent` per guideline §2 |
| `Open_House_time` | FINN_EIENDOM_001 | `open_house_schedule` |
| `About_14_Riverwood_Place` | DAFT.IE_002 | site-specific, should be `description` |
| `Vendu par` / French labels | LEBONCOIN_002 | should be translated to canonical EN names |
| `Land_area` / `Internal_use_area` | FINN_EIENDOM_002 | `land_area` / `floor_area` |

> [!IMPORTANT]
> The `location` field is used across **every single file** but the guideline maps `address / property_address / location → address`. This is a cross-domain consistency issue.

---

## ⚠️ Issue 3 — Bedroom/Bathroom Normalization (§1.3)

The guideline says counts should be **integers**:
```json
"bedrooms": { "value": "4 Bed", "normalized": 4 }
```

| File | Issues | Current format |
|------|--------|----------------|
| REDFIN_001_LISTING | ❌ 41/41 | string `"3"` not int |
| REALESTATE.CO.NZ_002_DETAIL | ❌ 1 | string not int |
| RIGHTMOVE_001_LISTING | ❌ 21/25 | string `"9"` not int |
| RIGHTMOVE_002_DETAIL | ❌ 1 | string `"1"` not int |

---

## ⚠️ Issue 4 — Date Normalization (§1.1)

The guideline requires:
- **Only real exact dates** (no relative dates like "yesterday", "3 days ago")
- ISO 8601 format in `normalized`

| File | Issues | Detail |
|------|--------|--------|
| RIGHTMOVE_001_LISTING | ❌ 2 records | `normalized: "yesterday"` — relative date, should be `null` per guideline |
| RIGHTMOVE_002_DETAIL | ✅ | `published date` normalized to `"2024-03-22"` ✅ |
| All others | ✅ | No date issues found |

> [!WARNING]
> Records with `"yesterday"` in `published_date.normalized` violate guideline §1.1. These should either be set to `null` or resolved from the snapshot's capture date.

---

## ⚠️ Issue 5 — Provenance Selector Quality (§3)

The guideline requires:
- `css_selector` = **stable** semantic selector (e.g., `[data-testid='price']`)
- `css_selector_absolute` = long nth-of-type chain (backup only)

Current state: **most selectors are absolute path chains** used as the primary selector. Example from RIGHTMOVE_001:
```json
"css_selector": "div#l-searchResults > div:nth-of-type(2) > div:nth-of-type(1) > div > a"
```

This should be the `css_selector_absolute`. The primary `css_selector` should be a stable semantic one. Additionally, **no files include `css_selector_absolute` or `xpath_absolute`** as separate backup fields.

---

## ⚠️ Issue 6 — Missing `attribute` field in Provenance (§3, §4.2)

For URL, image, and meta fields, provenance should include `"attribute": "href"` or `"attribute": "src"`. Currently, all provenance blocks omit the `attribute` field entirely.

---

## ✅ What Is Done Well

| Aspect | Status |
|--------|--------|
| All files have `records`, `schema_id`, `snapshot_id`, `live_url` | ✅ |
| All records have `provenance` block | ✅ |
| `human_verified` status on all files | ✅ |
| ISO date normalization implemented in detail files | ✅ |
| `£` symbol preserved (not escaped as `\u00a3`) | ✅ |
| Consistent `gold_record_id` naming convention | ✅ |
| `notes` field present in newer files | ✅ |

---

## Summary — Priority Fix List

| Priority | Issue | Files Affected | Effort |
|----------|-------|----------------|--------|
| 🔴 High | Price `normalized` must be dict (amount + currency) | 14/20 files | Medium |
| 🔴 High | `location` → rename to `address` | All 20 files | Low |
| 🟡 Medium | `beedrooms`, `BEDROOMS`, `listed_by`, mixed-case field names | 5+ files | Low |
| 🟡 Medium | Bedroom/bathroom `normalized` must be `int`, not `string` | 4 files | Low |
| 🟡 Medium | Relative dates (`"yesterday"`) must be `null` | RIGHTMOVE_001 | Low |
| 🟠 Low | Add `css_selector_absolute`, `xpath_absolute`, `attribute` to provenance | All files | High |
| 🟠 Low | Use stable semantic CSS selectors as primary (not absolute paths) | All files | High |
| 🟠 Low | Translate non-English field names (LEBONCOIN, FINN_EIENDOM) | 2 files | Medium |

---

# Recommended Field-Name Standardization

Derived from all field names observed across the **570 records / 20 gold files** of the real estate domain. All names follow `snake_case` and are aligned with the annotation guideline §2.

---

## Core Listing Fields (all task types)

| Canonical Name | Current Variants Found | Files Using Variants | Notes |
|---|---|---|---|
| `listing_url` | `listing_url` | All | ✅ Already consistent |
| `listing_title` | `listing_title`, `title` | FINN_EIENDOM, MAROC_ANNONCES, ONTHEMARKET, REALESTATE.CO.NZ | Use `listing_title` |
| `address` | `location`, `address` | All (15 files use `location`) | 🔴 Rename `location` → `address` |
| `description` | `description`, `short_description`, `About_14_Riverwood_Place`, `about_this_home` | Multiple | Use `description` for primary; `short_description` only if a separate short version exists |
| `price` | `price`, `Price`, `Prix du bien` | Multiple | ✅ `price` is canonical; translate French/Norwegian variants |
| `property_type` | `property_type`, `type`, `Type`, `type_house`, `Housing_type`, `Type de bien` | Multiple | Use `property_type` |
| `bedrooms` | `bedrooms`, `beds`, `beedrooms`, `Bedroom`, `Total_Bedrooms`, `Nombre de chambres` | Multiple | 🔴 All → `bedrooms` |
| `bathrooms` | `bathrooms`, `Total_Bathrooms`, `Total_bathrooms`, `Nombre de salles d'eau` | Multiple | 🔴 All → `bathrooms` |
| `floor_area` | `floor_area`, `area`, `sq_ft`, `Sq_Ft`, `sq._ft.`, `Square_Feet`, `Use_Area`, `Internal_use_area`, `Surface habitable` | Multiple | Use `floor_area`; add `unit` field (`m2` or `sqft`) |
| `land_area` | `land_area`, `Land_area`, `lot_size` | REDFIN, REALESTATE.CO.NZ, FINN_EIENDOM | Use `land_area`; add `unit` |
| `images_urls` | `images_urls`, `image_url`, `image` | Multiple | Use `images_urls` (always a list) |
| `published_date` | `published_date`, `published date` (space), `published_day`, `published_or_posted`, `Date_listed` | Multiple | 🔴 Use `published_date`; normalize to ISO 8601 |
| `listing_agent` | `listed_by`, `agent`, `agent_listing`, `by`, `Vendu par` | Multiple | 🔴 All → `listing_agent` |
| `listing_office` | `agent_branding`, `agent_branding_name` | Multiple | Use `listing_office` for the company/agency name |
| `listing_agent_logo` | `agent_branding_logo`, `agent_logo`, `logo_agent` | Multiple | Use `listing_agent_logo` |
| `listing_agent_phone` | `agent_branding_phone`, `agent_phone`, `phone`, `agent_branding_negotiator_phone` | Multiple | Use `listing_agent_phone` |
| `listing_agent_location` | `agent_branding_location` | RIGHTMOVE | Use `listing_agent_location` |
| `listing_agent_photo` | `agent_branding_negotiator_pic` | REALESTATE.CO.NZ | Use `listing_agent_photo` |
| `listing_agent_name` | `agent_branding_negotiator_name` | DAFT.IE, REALESTATE.CO.NZ, MAROC_ANNONCES | Use `listing_agent_name` for individual negotiator name |
| `listing_agent_website` | `agent_website` | ONTHEMARKET | Use `listing_agent_website` |

---

## Property Attributes

| Canonical Name | Current Variants Found | Notes |
|---|---|---|
| `energy_rating` | `energy_rating`, `BER_energy_rating`, `ATG_energy_Marking`, `EPC_rating`, `Classe énergie`, `Energy_Performance` | Use `energy_rating`; normalize to label only (e.g., `"B3"`) |
| `parking` | `PARKING`, `parking_or_garage_spaces`, `Parking_Features`, `Parking_description` | Use `parking`; normalize to boolean or count |
| `furnish_type` | `Furnish type` (space) | 🔴 Use `furnish_type` |
| `key_features` | `Key features` (space), `key_features`, `features`, `Features_description` | Use `key_features` (list of strings) |
| `rooms` | `rooms`, `Room`, `Number_of_Rooms`, `Nombre de pièces` | Use `rooms` (integer) |
| `year_built` | `year_built`, `Year_Built`, `Year_built`, `Year_of_construction` | Use `year_built` (integer) |
| `floor_level` | `Etage` | Use `floor_level` |
| `ownership_type` | `ownership_type`, `tenure`, `Selling_Type` | Use `tenure`; normalize to `"freehold"` / `"leasehold"` |
| `open_house_schedule` | `open_time`, `Open_House_time` | Use `open_house_schedule` |
| `total_price` | `total_price`, `Total_price`, `Total_price` | Use `total_price` (for Scandinavian markets with joint debt included) |
| `monthly_fees` | `monthly_fees`, `Common_cost_mn`, `costs` | Use `monthly_fees` |
| `price_per_m2` | `price_per_m2`, `Price_per_m²`, `Price_per_sq.__ft._` | Use `price_per_m2`; add `unit` |
| `status` | `status`, `Status` | Use `status`; normalize to canonical values (`"for_sale"`, `"for_rent"`, `"sold"`) |
| `sale_type` | `sale_type`, `Selling_Type` | Use `sale_type` |

---

## Review / Rating Fields (Detail pages only)

| Canonical Name | Current Variants Found | Notes |
|---|---|---|
| `rating` | `rating` | ✅ Good |
| `review_count` | `review_count` | ✅ Good; normalize to integer |
| `reviews` | `first review` (space) | 🔴 Use `reviews` (list); each item has sub-fields below |
| `reviews[].rating` | `rating` inside first review | Use float (e.g., `5.0`) |
| `reviews[].person_name` | `person_name` | ✅ Good |
| `reviews[].date` | `date review` (space) | 🔴 Use `reviews[].date`; normalize to ISO (`YYYY-MM` or `YYYY-MM-DD`) |
| `reviews[].title` | `title` inside first review | ✅ Good |
| `reviews[].content` | `review_content` | Use `reviews[].content` |

---

## Structured / Nested Fields

| Canonical Name | Current Variants Found | Notes |
|---|---|---|
| `property_details` | `property_details` | ✅ Good (nested JSON with interior/exterior sub-objects) |
| `public_record` | `public_record` | ✅ Good |
| `around_this_home` | `around_this_home` | ✅ Good (schools, transit, places as nested JSON) |
| `price_history` | `Price_&_Sales_History` | Use `price_history` |
| `tax_history` | `Tax_History` | Use `tax_history` |
| `schools` | `Schools`, `Local_schools_and_transport` | Use `schools` (list of structured objects) |
| `map` | `map` | Consider `map_embed_url` or drop if non-extractable |

---

## Fields to Drop or Avoid

| Field | Reason |
|---|---|
| `Views` | Site-internal metric, not property data |
| `Source`, `Sq._Ft._Source` | Internal metadata, not extractable content |
| `Reference` | Platform-internal ID; use `listing_id` instead |
| `annonce_id` | Use `listing_id` instead |
| `map` | Embedded map widget, not a text field |
| `Special_Conditions`, `Road_Maintenance`, `Sewer`, `Water`, `Windows`, `Roof` | Too granular; group into `property_details.exterior` |
| French / Norwegian raw labels | Always translate to canonical English snake_case |

---

## Summary Table — Canonical Field Set

```text
Core:
  listing_url, listing_title, address, description, price, published_date,
  property_type, status, sale_type, tenure

Property attributes:
  bedrooms, bathrooms, floor_area, land_area, rooms, year_built,
  parking, furnish_type, floor_level, energy_rating,
  key_features, open_house_schedule

Financials:
  total_price, monthly_fees, price_per_m2

Media:
  images_urls

Agent:
  listing_agent, listing_office, listing_agent_logo, listing_agent_phone,
  listing_agent_location, listing_agent_photo, listing_agent_name,
  listing_agent_website

Reviews (detail pages):
  rating, review_count, reviews[]

Structured (detail pages):
  property_details, public_record, around_this_home,
  price_history, tax_history, schools
```
