Below is the final WADE-Bench annotation guideline based on what we discussed.

# 1. Normalization rules

Main rule:

```text
value = clean extracted value from the page
normalized = machine-readable standard value
text_quote = exact evidence from the HTML/page
```

Do **not** keep labels inside `value`.

Bad:

```json
"listing_agent": {
  "value": "Listed by Ahmed",
  "normalized": "Listed by Ahmed"
}
```

Good:

```json
"listing_agent": {
  "value": "Ahmed",
  "normalized": "Ahmed"
}
```

The full page text goes only in provenance:

```json
"text_quote": "Listed by Ahmed"
```

---

## 1.1 Date / datetime

Use only **real exact dates/times**.

Use ISO 8601 for `normalized`.

```json
"listed_datetime": {
  "value": "05-28-2026 07:18 PM",
  "normalized": "2026-05-28T19:18:00"
}
```

With timezone if known:

```json
"listed_datetime": {
  "value": "05-28-2026 07:18 PM",
  "normalized": "2026-05-28T19:18:00-07:00"
}
```

Do **not** use these fields:

```json
"posted_relative": {}
"listed_relative": {}
"days_on_site": {}
```

Do **not** extract vague/relative dates like:

```text
Listed now
Added to Site 15 day(s) ago
Posted today
3 hours ago
```

If the page only gives relative date, skip the date field or set it to null if required by schema:

```json
"listed_datetime": {
  "value": null,
  "normalized": null
}
```

---

## 1.2 Price

Use clean price value and normalized amount + currency.

```json
"price": {
  "value": "$1,299,000",
  "normalized": {
    "amount": 1299000.0,
    "currency": {
      "name": "US dollar",
      "code": "USD",
      "symbol": "$"
    }
  }
}
```

For UK:

```json
"price": {
  "value": "£475,000",
  "normalized": {
    "amount": 475000.0,
    "currency": {
      "name": "British pound",
      "code": "GBP",
      "symbol": "£"
    }
  }
}
```

For Europe:

```json
"price": {
  "value": "€395,000",
  "normalized": {
    "amount": 395000.0,
    "currency": {
      "name": "Euro",
      "code": "EUR",
      "symbol": "€"
    }
  }
}
```

---

## 1.3 Numbers

Counts should be integers.

```json
"bedrooms": {
  "value": "4 Bed",
  "normalized": 4
}
```

```json
"bathrooms": {
  "value": "2 Bath",
  "normalized": 2
}
```

Decimal values should be floats.

```json
"floor_area": {
  "value": "145 m²",
  "normalized": 145.0,
  "unit": "m2"
}
```

```json
"land_area": {
  "value": "1051m²",
  "normalized": 1051.0,
  "unit": "m2"
}
```

```json
"lot_size": {
  "value": "0.0733 acres",
  "normalized": 0.0733,
  "unit": "acre"
}
```

---

## 1.4 URLs

URLs should be absolute.

```json
"listing_url": {
  "value": "https://www.realestate.co.nz/43058132/residential/sale/600-park-road-north-parkvale",
  "normalized": "https://www.realestate.co.nz/43058132/residential/sale/600-park-road-north-parkvale"
}
```

If the HTML gives a relative URL:

```json
"listing_url": {
  "value": "/43058132/residential/sale/600-park-road-north-parkvale",
  "normalized": "https://www.realestate.co.nz/43058132/residential/sale/600-park-road-north-parkvale"
}
```

---

## 1.5 Boolean fields

Use true / false.

```json
"has_swimming_pool": {
  "value": "Swimming pool icon shown",
  "normalized": true
}
```

```json
"is_furnished": {
  "value": "Unfurnished",
  "normalized": false
}
```

---

## 1.6 Category fields

Use lowercase canonical form.

```json
"property_type": {
  "value": "Detached",
  "normalized": "detached"
}
```

```json
"property_type": {
  "value": "House",
  "normalized": "house"
}
```

```json
"tenure": {
  "value": "Leasehold",
  "normalized": "leasehold"
}
```

```json
"energy_rating": {
  "value": "BER B3",
  "normalized": "B3"
}
```

---

## 1.7 Identifiers and reference numbers

Identifiers should remain **strings**, even when they look numeric.

Do **not** convert identifiers to integers or floats, because IDs may contain leading zeros, letters, dashes, or platform-specific formats.

Bad:

```json
"mls_number": {
  "value": "426138391",
  "normalized": 426138391
}
```

Good:

```json
"mls_number": {
  "value": "426138391",
  "normalized": "426138391"
}
```

Use this rule:

```text
Counts → integer
Measurements → float + unit
Prices → amount + currency
Identifiers → string
```

Examples of identifier fields that should stay as strings:

```text
mls_number
listing_id
reference_id
property_id
apn
parcel_number
cadastral_reference
sku
contract_reference
```

---

# 2. Field-name standardization

Use one canonical field name for the same meaning across all websites.

Use `snake_case`.

## Good canonical names

```text
beds / bed / bedroom_count / number_of_bedrooms → bedrooms
baths / bath / bathroom_count / number_of_bathrooms → bathrooms
sqft / floor_size / living_area / internal_area → floor_area
land / plot_size / lot_area / land_size → land_area
price / asking_price / listing_price → price
address / property_address / location → address
agent / listed_by / broker_name → listing_agent
office / brokerage / agency → listing_office
open house / viewing time → open_house_schedule
BER / energy class / energy rating → energy_rating
MLS_Number / MLS# / MLS No. / mlsNumber → mls_number
Reference / annonce_id / property_id → listing_id
```

Do not use duplicate fields like:

```text
bed
beds
bedrooms_count
number_of_bedrooms
```

Use only:

```text
bedrooms
```

---

# 3. Provenance rules

Each field should have provenance.

Use this structure:

```json
"provenance": {
  "field_name": {
    "snapshot_id": "SNAP_REAL_RIGHTMOVE_002_DETAIL",
    "css_selector": "stable selector",
    "css_selector_absolute": "absolute backup selector",
    "xpath": "stable xpath",
    "xpath_absolute": "absolute backup xpath",
    "attribute": null,
    "text_quote": "exact text from page"
  }
}
```

Main rule:

```text
css_selector = stable selector for evaluation
css_selector_absolute = backup/debug selector
xpath = stable XPath for evaluation
xpath_absolute = backup/debug XPath
```

---

## 3.1 Good CSS selector strategy

Prefer stable attributes:

```css
[data-test='price-display__price-method']
```

```css
[data-test='bedroom']
```

```css
link[rel='canonical']
```

```css
[data-tracking='srp_ber'][aria-label]
```

Avoid generic selectors:

```css
img
p
div
svg
```

Avoid using only generated classes:

```css
.sc-620b3daf-0
.ember-view
.text-slateGrey-500
```

Avoid using long absolute selectors as the main selector:

```css
main#main > div > div:nth-of-type(3) > div > div:nth-of-type(1) > div:nth-of-type(1) > div > h1
```

You can keep this only as:

```json
"css_selector_absolute": "..."
```

---

## 3.2 Provenance for identifiers

Identifiers such as `mls_number`, `listing_id`, `reference_id`, `property_id`, `apn`, and `parcel_number` should have provenance like any other field.

The identifier value stays a **string** in the field value, but provenance should preserve the exact evidence from the page.

Example field:

```json
"mls_number": {
  "value": "426138391",
  "normalized": "426138391"
}
```

Example provenance when the identifier is visible text:

```json
"mls_number": {
  "snapshot_id": "SNAP_REAL_001_DETAIL",
  "css_selector": "main .property-details [data-testid='mls-number']",
  "css_selector_absolute": "main > div:nth-of-type(3) dl > div:nth-of-type(4) dd",
  "xpath": "//main//*[contains(@data-testid,'mls-number')]",
  "xpath_absolute": "//html/body/main/div[3]//dl/div[4]/dd",
  "attribute": null,
  "text_quote": "MLS# 426138391"
}
```

Example provenance when the identifier is stored in an HTML attribute:

```json
"listing_id": {
  "snapshot_id": "SNAP_REAL_001_LISTING",
  "css_selector": "article[data-listing-id='71582925']",
  "css_selector_absolute": "article:nth-of-type(1)",
  "xpath": "//article[@data-listing-id='71582925']",
  "xpath_absolute": "//article[1]",
  "attribute": "data-listing-id",
  "text_quote": null
}
```

Identifier provenance rule:

```text
For visible identifier text:
  attribute = null
  text_quote = exact page text, including label if present

For identifier stored in an attribute:
  attribute = the attribute name, e.g. data-listing-id, value, content, href
  text_quote = null unless visible text is also present

For identifier extracted from JSON-LD or script:
  css_selector = stable script selector when available
  xpath = stable script XPath when available
  attribute = null
  text_quote = shortest exact JSON/script snippet containing the identifier
```

Bad provenance:

```json
"mls_number": {
  "css_selector": "div",
  "xpath": "//div",
  "text_quote": "426138391"
}
```

Good provenance:

```json
"mls_number": {
  "css_selector": "[data-testid='mls-number']",
  "xpath": "//*[@data-testid='mls-number']",
  "attribute": null,
  "text_quote": "MLS# 426138391"
}
```

The selector must still be unique:

```text
Identifier selector should select only the identifier field inside the target record/page.
Do not use a broad selector that selects all metadata rows or all listing cards.
```

---

# 4. Provenance examples

## 4.1 Address / location

```json
"address": {
  "snapshot_id": "SNAP_REAL_RIGHTMOVE_002_DETAIL",
  "css_selector": "main#main h1",
  "css_selector_absolute": "main#main > div > div:nth-of-type(3) > div > div:nth-of-type(1) > div:nth-of-type(1) > div > h1",
  "xpath": "//main[@id='main']//h1",
  "xpath_absolute": "//html/body[1]/div[2]/main[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/h1[1]",
  "attribute": null,
  "text_quote": "The Lansdowne, 25 Hagley Road,"
}
```

## 4.2 Listing URL

For URL fields, use `attribute: "href"`.

```json
"listing_url": {
  "snapshot_id": "SNAP_REAL_RIGHTMOVE_002_DETAIL",
  "css_selector": "link[rel='canonical']",
  "css_selector_absolute": "html > head > link:nth-of-type(7)",
  "xpath": "//link[@rel='canonical']",
  "xpath_absolute": "//html/head[1]/link[7]",
  "attribute": "href",
  "text_quote": null
}
```

Do not use only:

```json
"css_selector": "html > head > link:nth-of-type(7)"
```

as the main selector. Keep it as backup only.

## 4.3 Image URL

For image/meta fields, use `attribute: "src"` or `attribute: "content"`.

```json
"primary_image_url": {
  "snapshot_id": "SNAP_REAL_RIGHTMOVE_002_DETAIL",
  "css_selector": "meta[property='og:image']",
  "css_selector_absolute": "html > head > meta:nth-of-type(12)",
  "xpath": "//meta[@property='og:image']",
  "xpath_absolute": "//html/head[1]/meta[12]",
  "attribute": "content",
  "text_quote": null
}
```

For normal image:

```json
"primary_image_url": {
  "snapshot_id": "SNAP_REAL_001_LISTING",
  "css_selector": "article img[src*='images-listings']",
  "css_selector_absolute": "article:nth-of-type(1) img:nth-of-type(1)",
  "xpath": "//article[1]//img[contains(@src,'images-listings')]",
  "xpath_absolute": "//article[1]//img[1]",
  "attribute": "src",
  "text_quote": null
}
```

## 4.4 Agent name

Page text:

```text
Listed by Ahmed
```

Field value:

```json
"listing_agent": {
  "value": "Ahmed",
  "normalized": "Ahmed"
}
```

Provenance:

```json
"listing_agent": {
  "snapshot_id": "SNAP_REAL_001_DETAIL",
  "css_selector": "[data-testid='agent-name']",
  "css_selector_absolute": "main > div:nth-of-type(3) span:nth-of-type(1)",
  "xpath": "//*[@data-testid='agent-name']",
  "xpath_absolute": "//main/div[3]//span[1]",
  "attribute": null,
  "text_quote": "Listed by Ahmed"
}
```

## 4.5 BER / energy rating

HTML:

```html
<div aria-label="BER B3" data-tracking="srp_ber"></div>
```

Field:

```json
"energy_rating": {
  "value": "BER B3",
  "normalized": "B3"
}
```

Provenance:

```json
"energy_rating": {
  "snapshot_id": "SNAP_REAL_LISTING_001",
  "css_selector": "[data-tracking='srp_ber'][aria-label]",
  "css_selector_absolute": "article:nth-of-type(1) div[data-tracking='srp_ber']",
  "xpath": "//*[@data-tracking='srp_ber' and @aria-label]",
  "xpath_absolute": "//article[1]//div[@data-tracking='srp_ber'][1]",
  "attribute": "aria-label",
  "text_quote": "BER B3"
}
```


## 4.6 MLS number / listing identifier

Page text:

```text
MLS# 426138391
```

Field:

```json
"mls_number": {
  "value": "426138391",
  "normalized": "426138391"
}
```

Provenance:

```json
"mls_number": {
  "snapshot_id": "SNAP_REAL_001_DETAIL",
  "css_selector": "[data-testid='mls-number']",
  "css_selector_absolute": "main > div:nth-of-type(3) dl > div:nth-of-type(4) dd",
  "xpath": "//*[@data-testid='mls-number']",
  "xpath_absolute": "//html/body/main/div[3]//dl/div[4]/dd",
  "attribute": null,
  "text_quote": "MLS# 426138391"
}
```

If the ID is in an attribute:

```json
"listing_id": {
  "snapshot_id": "SNAP_REAL_001_LISTING",
  "css_selector": "article[data-listing-id='71582925']",
  "css_selector_absolute": "article:nth-of-type(1)",
  "xpath": "//article[@data-listing-id='71582925']",
  "xpath_absolute": "//article[1]",
  "attribute": "data-listing-id",
  "text_quote": null
}
```

---

---

# 5. Full final example

```json
{
  "record_id": "REAL_REALESTATECO_001_001",
  "record_type": "real_estate_listing",
  "fields": {
    "listing_url": {
      "value": "https://www.realestate.co.nz/43058132/residential/sale/600-park-road-north-parkvale",
      "normalized": "https://www.realestate.co.nz/43058132/residential/sale/600-park-road-north-parkvale"
    },
    "address": {
      "value": "600 Park Road North, Parkvale",
      "normalized": "600 Park Road North, Parkvale"
    },
    "listing_title": {
      "value": "Timeless Character, Modern Comfort",
      "normalized": "Timeless Character, Modern Comfort"
    },
    "price": {
      "value": "$1,299,000",
      "normalized": {
        "amount": 1299000.0,
        "currency": {
          "name": "New Zealand dollar",
          "code": "NZD",
          "symbol": "$"
        }
      }
    },
    "bedrooms": {
      "value": "4",
      "normalized": 4
    },
    "bathrooms": {
      "value": "2",
      "normalized": 2
    },
    "land_area": {
      "value": "1051m²",
      "normalized": 1051.0,
      "unit": "m2"
    },
    "property_type": {
      "value": "House",
      "normalized": "house"
    },
    "has_swimming_pool": {
      "value": "Swimming pool icon shown",
      "normalized": true
    },
    "listed_datetime": {
      "value": null,
      "normalized": null
    }
  },
  "provenance": {
    "listing_url": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "a[href*='/43058132/residential/sale/']",
      "css_selector_absolute": "div.search-results > div:nth-of-type(1) > a",
      "xpath": "//a[contains(@href, '/43058132/residential/sale/')]",
      "xpath_absolute": "//div[contains(@class,'search-results')]/div[1]/a[1]",
      "attribute": "href",
      "text_quote": null
    },
    "address": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='premium-tile__search-result__address']",
      "css_selector_absolute": "a:nth-of-type(1) h3",
      "xpath": "//*[@data-test='premium-tile__search-result__address']",
      "xpath_absolute": "//a[1]//h3[1]",
      "attribute": null,
      "text_quote": "600 Park Road North, Parkvale"
    },
    "listing_title": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='tile__search-result__content__description'] h4",
      "css_selector_absolute": "a:nth-of-type(1) h4",
      "xpath": "//*[@data-test='tile__search-result__content__description']//h4",
      "xpath_absolute": "//a[1]//h4[1]",
      "attribute": null,
      "text_quote": "Timeless Character, Modern Comfort"
    },
    "price": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='price-display__price-method']",
      "css_selector_absolute": "a:nth-of-type(1) [data-test='price-display__price-method']",
      "xpath": "//*[@data-test='price-display__price-method']",
      "xpath_absolute": "//a[1]//*[@data-test='price-display__price-method'][1]",
      "attribute": null,
      "text_quote": "$1,299,000"
    },
    "bedrooms": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='bedroom']",
      "css_selector_absolute": "a:nth-of-type(1) [data-test='bedroom']",
      "xpath": "//*[@data-test='bedroom']",
      "xpath_absolute": "//a[1]//*[@data-test='bedroom'][1]",
      "attribute": null,
      "text_quote": "4"
    },
    "bathrooms": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='bathroom']",
      "css_selector_absolute": "a:nth-of-type(1) [data-test='bathroom']",
      "xpath": "//*[@data-test='bathroom']",
      "xpath_absolute": "//a[1]//*[@data-test='bathroom'][1]",
      "attribute": null,
      "text_quote": "2"
    },
    "land_area": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='land-area']",
      "css_selector_absolute": "a:nth-of-type(1) [data-test='land-area']",
      "xpath": "//*[@data-test='land-area']",
      "xpath_absolute": "//a[1]//*[@data-test='land-area'][1]",
      "attribute": null,
      "text_quote": "1051m²"
    },
    "property_type": {
      "snapshot_id": "SNAP_REAL_REALESTATECO_001_LISTING",
      "css_selector": "[data-test='tile__search-result__content__features__divider']",
      "css_selector_absolute": "a:nth-of-type(1) [data-test='tile__search-result__content__features__divider']",
      "xpath": "//*[@data-test='tile__search-result__content__features__divider']",
      "xpath_absolute": "//a[1]//*[@data-test='tile__search-result__content__features__divider'][1]",
      "attribute": null,
      "text_quote": "House"
    }
  }
}
```

Final summary:

```text
1. Use clean canonical field names.
2. value = clean extracted value, not label text.
3. normalized = typed machine-readable value.
4. text_quote = exact evidence from page.
5. Use stable selector + absolute backup selector.
6. Use attribute for URL, image, meta, aria-label fields.
7. Do not extract relative dates; only exact date/time in ISO format.
8. Keep identifiers as strings, even if they look numeric.
9. Identifier provenance must point to the exact ID element or attribute.
```
