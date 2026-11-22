# WADE-Bench fixed runner

This package supports running one baseline with one model at a time, then scoring and aggregating later.

## Install

```powershell
cd path\to\wadebench_fixed_project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For local models, Ollama must be running and models must be pulled:

```powershell
ollama list
ollama pull gemma4:e4b
ollama pull qwen3-vl:8b
```

For Kimi K2.6 API:

```powershell
$env:MOONSHOT_API_KEY="YOUR_KIMI_API_KEY"
```

## Required data layout

The scripts expect:

- a task split JSONL file, e.g. `data/tasks/wadebench_v1_5domains.jsonl`
- schema files in `data/schemas/{schema_id}.json`
- gold files referenced by `gold_path` in each task, or discoverable via `--gold-root`

Each task line should include at least:

```json
{
  "task_id": "WBV1_ECOM_01_IKEA_US_LISTING",
  "domain": "ecommerce",
  "task_type": "listing",
  "schema_id": "product_listing_v1",
  "snapshot_path": "data/snapshots/...",
  "source_files": {
    "page_html": "data/snapshots/.../page.html",
    "page_safe_html": "data/snapshots/.../page.safe.html",
    "screenshot": "data/snapshots/.../screenshot.png",
    "text_txt": "data/snapshots/.../text.txt",
    "ax_tree": "data/snapshots/.../ax_tree.json",
    "metadata": "data/snapshots/.../metadata.json"
  },
  "gold_path": "data/gold/by_task/ecommerce/WBV1_ECOM_01_IKEA_US_LISTING.json"
}
```

## Task success metric

Default task success is:

```text
record_recall >= 0.90 AND field_f1 >= 0.85 AND schema_adherence == 1
```

You can change thresholds in `scripts/score_predictions.py` using:

```powershell
--record-recall-threshold 0.90 --field-f1-threshold 0.85
```

## Important note about B3 + Gemma

Your local sanity test showed `qwen3-vl:8b` can read screenshots, while `gemma4:e4b` and `gemma4-131k` failed the same image-reading test. Therefore, use Gemma for B1/B2/B4 text/evidence baselines only. B3 + Gemma can run technically, but it is not recommended for final paper results unless you add OCR or a valid Gemma vision configuration.


## Provenance locator policy

The evaluator now checks all four locator fields:

- `css_selector`
- `xpath`
- `css_selector_absolute`
- `xpath_absolute`

Reported selector metrics:

- `semantic_selector_coverage`: `css_selector` or `xpath` present.
- `absolute_selector_coverage`: `css_selector_absolute` or `xpath_absolute` present.
- `selector_coverage`: any of the four locator fields present.

Semantic/short locators are preferred. Absolute locators are treated as fallback evidence.

Recommended model set:

- Use `gemma4:e4b` with `--num-ctx 131072`.
- Do not count `gemma4-131k:latest` as a separate LLM if it has the same architecture, parameter count, quantization, and context length as `gemma4:e4b`.
- Use `qwen3-vl:8b` for local vision baseline.
- Use `kimi-k2.6` through API for the paid model condition.


## Kimi API key via .env

The project supports a local `.env` file. Copy `.env.example` to `.env` and add your real Kimi/Moonshot API key:

```powershell
Copy-Item .env.example .env
notepad .env
```

Inside `.env`:

```env
MOONSHOT_API_KEY=sk-your_kimi_api_key_here
```

The code automatically loads `.env` using `python-dotenv`. Do not commit or share `.env`; it is excluded by `.gitignore`.

## Scoring patch note — 2026-06-28

The evaluator intentionally compares field values using the raw `value` field and normalizes it at scoring time. Gold `normalized` values may still help record alignment when present, but field scoring remains symmetric between predictions and gold.

Patched evaluator behavior:
- List-valued fields are compared as order-insensitive multisets after item normalization, so `["c", "a", "b"]` matches `["a", "b", "c"]`.
- Leading currency codes now normalize correctly, so `USD 220`, `USD220`, `$220`, and `220 USD` match.
- Removed dead `wadebench/evaluator/normalize.py` passthrough module.
