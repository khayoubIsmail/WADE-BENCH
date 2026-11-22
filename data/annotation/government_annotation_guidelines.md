# Government Tender Notice Annotation Guidelines

These guidelines describe how to annotate tender notice records for the government/tenders/announcements domain.

## Required fields
- **tender_title**: The official title or description of the tender or procurement notice.
- **reference_number**: The unique notice or reference number identifying the tender.
- **buyer**: The organisation issuing the tender (e.g., ministry, department, agency).
- **tender_url**: The URL linking directly to the tender notice detail page.
- **publication_date**: The date the notice was published.
- **closing_date**: The deadline for receipt of tenders or responses.

## Optional fields
- **contract_value**: The estimated or actual contract value if provided.
- **currency**: The currency in which the contract value is denominated.
- **cpv_code**: Common Procurement Vocabulary code if provided.
- **location**: The city/region/country where the contract applies or work is to be carried out.
- **description**: A longer description of the procurement requirements.
- **contact_person**: Contact information for enquiries.
- **documents_url**: Links to documents (tender documents, specifications, etc.).

## Provenance
For each field, record the XPath or CSS selector pointing to the source element on the page. Use absolute URLs for tender_url.
