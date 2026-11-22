# Real Estate Annotation Guidelines

"
        "These guidelines describe how to annotate real estate property listings for
"
        "WADE‑Bench v1. The goal is to provide high‑quality, structured ground truth
"
        "records for each property that appears on the listing and detail pages.

"
        "## Required fields

"
        "* **listing_title**: Use the main title of the property listing.
"
        "* **price**: Extract the numeric price only, without currency symbols. Use the
"
        "  currency information implicitly from the page.
"
        "* **location**: Include city/town and region (e.g. 'Casablanca, Morocco').
"
        "* **property_type**: Category such as 'House', 'Apartment', 'Villa', etc.
"
        "* **listing_url**: The canonical URL of the listing.

"
        "## Optional fields

"
        "* **bedrooms** and **bathrooms**: Integer values when present.
"
        "* **area**: Size of the property in square meters (m²).
"
        "* **floor**: Floor number for apartments, if provided.
"
        "* **latitude** and **longitude**: Geographic coordinates if available.
"
        "* **listing_date**: ISO 8601 date (YYYY‑MM‑DD) when the property was listed.
"
        "* **agent**: Name of the listing agent or agency.
"
        "* **description**: Full textual description of the property.
"
        "* **images**: List of image URLs.

"
        "## Provenance

"
        "Annotators must provide an XPath or CSS selector for each field they extract.
"
        "The selector should point to the specific HTML element containing the data.
"
        "This ensures that the extraction can be reproduced precisely during evaluation.

"
        "## Normalization rules

"
        "* **Price**: Remove currency symbols and thousand separators. Example: '€1,250,000'
"
        "  becomes '1250000'.
"
        "* **Area**: Convert to square meters if the site uses other units (e.g. square feet).
"
        "* **Listing date**: Format as YYYY‑MM‑DD.
"
        "* **Latitude/Longitude**: Provide as floating‑point numbers with at least 5 decimal places.

"
        "## Quality control

"
        "* Validate every record against the schema before submission.
"
        "* Use a secondary annotator to spot‑check at least 20% of records.
"
        "* Record any ambiguities or edge cases in a separate notes file for discussion.
"
        