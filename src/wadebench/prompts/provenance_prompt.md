# Provenance Prompt

Use this template to capture field-level provenance for WADE-Bench predictions.

For every non-null extracted field, include a provenance object with:

```json
{
  "source": "page.html",
  "css_selector": null,
  "xpath": null,
  "css_selector_absolute": null,
  "xpath_absolute": null,
  "bbox": null,
  "text_quote": "short supporting quote"
}
```

Locator meaning:

- `css_selector`: preferred short/semantic CSS selector.
- `xpath`: preferred short/semantic XPath.
- `css_selector_absolute`: fallback absolute CSS selector.
- `xpath_absolute`: fallback absolute XPath.

Evaluation reports three selector metrics:

- `semantic_selector_coverage`: `css_selector` or `xpath` present.
- `absolute_selector_coverage`: `css_selector_absolute` or `xpath_absolute` present.
- `selector_coverage`: any of the four locator fields present.

Absolute selectors count as fallback evidence, but semantic selectors are preferred for provenance quality.
