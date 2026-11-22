# WADE-Bench v1 Jobs Domain Annotation Guidelines

These guidelines describe how to annotate job posting data for the WADE-Bench v1 benchmark. Each record corresponds to a single job listing. Annotators should read the page snapshot (listing or detail) and fill out the fields defined in `job_posting_v1.json`. Always capture the selector (XPath or CSS) that points to the source of each field.

## Required fields

- **job_title**: The exact title of the job. Prefer the main heading of the listing. Do not abbreviate.
- **company_name**: The name of the hiring organisation or company. Use the brand name as displayed.
- **location**: City, region, and country (if provided). Use the normalised format (e.g., `Casablanca, Morocco`). If multiple locations are listed, separate them with semicolons.
- **job_url**: The canonical URL to the job description page. When annotating listing pages, capture the link to the job detail page.

## Optional fields

- **employment_type**: Whether the position is full-time, part-time, contract, freelance, etc. If multiple options are listed, choose the primary type.
- **salary_range**: Provide the salary range as shown (e.g., `$80,000 – $100,000 per year`). If only one value is given, annotate that value.
- **posted_date**: The date when the job was posted. Convert to `YYYY-MM-DD` format.
- **closing_date**: The application deadline, if specified. Convert to `YYYY-MM-DD` format.
- **job_description**: A concise summary of the role’s responsibilities and mission. Include the main paragraph or bullet points.
- **requirements**: Key qualifications or requirements listed for the role, such as skills, education level, or years of experience.
- **benefits**: List any benefits or perks described in the job posting, such as health insurance, remote work, stock options.

## Provenance

For each field, provide the XPath or CSS selector that pinpoints the source element in the HTML. Example:

```
{
  "field": "job_title",
  "selector": "//h1[@class='job-title']",
  "value": "Senior Software Engineer"
}
```

## Normalisation rules

- Normalise dates to ISO format (`YYYY-MM-DD`).
- For salaries, preserve the currency symbol and use the same notation shown on the page.
- Locations should follow `City, Region, Country` with comma separation.

## Common pitfalls

- Some listing pages display salary range or employment type only on the detail page. If not visible on the listing page, leave the field empty until detail extraction.
- Company names sometimes appear with additional text like “Ltd.” or “Inc.”; include these if present.
- Do not invent values; leave optional fields blank if not available.

