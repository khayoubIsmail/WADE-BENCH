# WADE-Bench: A Schema-Guided Benchmark for Web Data Extraction Agents

WADE-Bench measures how well LLM-based systems **extract structured data from web pages**.
Each task gives a system a **frozen snapshot** of a web page and a **target schema**. The system must return **every record on the page** as schema-valid JSON, with **field-level provenance** (where each value was found).

Paper: *WADE-Bench: A Schema-Guided Benchmark for Web Data Extraction Agents*. Ismail Khayoub, Mohamed-Amine Chadi, Hajar Mousannif, Firdaous Ait Mohamed. MEDES 2026, Special Track on Trustworthy and Human-Centered AI for Web Information Systems.

**Main finding:** systems find most records (record F1 up to 0.91) but fill their fields far less reliably (strict field F1 at most 0.40). Finding records, filling fields correctly, and justifying them are three different capabilities.

---

## At a glance

| | |
|---|---|
| Domains | e-commerce, jobs, academic events, government tenders, real estate |
| Websites | 50 (10 per domain) |
| Tasks | 100 (50 listing pages + 50 detail pages) |
| Gold records | 1,955, human-verified, with normalised values and field-level provenance |
| Field slots | ~19.4k (about 18% null: value genuinely absent from the page) |
| Schemas | 10 (one listing + one detail schema per domain), 9–17 typed fields |
| Snapshot views | rendered HTML, visible text, full screenshot, accessibility tree, metadata, single-file archive |
| Baseline study | 4 input views × 3 models × 100 tasks = 1,200 runs |

## Task

A task is a tuple `(snapshot, domain, instruction, schema, allowed setting)`.

- **Listing task:** return all records on an index or search-results page.
- **Detail task:** return the richer field set of a single-entity page.
- *Listing-to-detail* (joining a listing with its detail pages) is defined but not populated in v1.

Expected output (simplified):

```json
{
  "records": [
    {
      "record_id": "pred_001",
      "fields": { "product_name": "Men's Dasher NZ", "price_raw": "$140", "category": null },
      "provenance": {
        "product_name": { "source": "page.html", "css_selector": "p.font-sans", "xpath": null, "text_quote": "Men's Dasher NZ" },
        "price_raw":    { "source": "page.html", "css_selector": "span.price",  "xpath": null, "text_quote": "$140" }
      }
    }
  ]
}
```

Rules: use only the snapshot (no live web, no outside knowledge); use `null` for values that are not on the page; give provenance for every non-null field.

## Metrics

| Metric | Question | Notes |
|---|---|---|
| **Record F1** | Did you find the records? | One-to-one alignment: URL match, then exact name, then normalised name, then a field-overlap fallback (threshold 0.5 in this release). Diagnostic only. |
| **Strict field F1** | Is each value right? | **Primary metric.** Typed, deterministic comparison (text, URL, date, money/salary, counts, measures, booleans, enums, lists). Invented values (gold null) lower precision; missing values lower recall; unmatched records still count. Micro-averaged over fields within a task, then averaged over the 100 tasks. |
| **Provenance** | Can the evidence be checked? | The selector must resolve in the frozen DOM, the quote must be inside that element and support the value (tile id for vision). |
| Schema validity | Valid JSON that follows the schema? | |
| Task success | Fully solved? | record recall ≥ 0.90, strict field F1 ≥ 0.85, schema-valid. |

Failed runs count as zero; every configuration is averaged over all 100 tasks.

## Baselines and models

| Baseline | Input given to the model |
|---|---|
| B1 HTML | cleaned `page.html` |
| B2 Markdown | page converted to Markdown text |
| B3 Vision | full screenshot cut into tiles (1,400 px, 180 px overlap, up to 24 tiles) |
| B4 Browser | accessibility tree + visible text + metadata, collected with `@playwright/mcp` (fixed tool sequence) |

Models: **Gemma 4 8B** (local, Ollama, Q4_K_M, 131k context; run under the local alias `gemma4-131k`, listed as *Local-8B-131k* in the paper), **Qwen2.5-VL 7B** (local, Ollama), **Kimi K2.6** (Moonshot API, thinking disabled). Temperature 0 for local models, 0.6 for Kimi. B1/B2 input budget: 200k characters (Qwen), 400k (Gemma), 600k (Kimi). One run per configuration.

## Results

| Baseline | Model | Record F1 | Strict field F1 | Provenance | Schema | Task success | Tokens (M) |
|---|---|---|---|---|---|---|---|
| B1 HTML | Kimi K2.6 | 0.8204 | **0.4019** | 0.7291 | 1.00 | **0.05** | 12.36 |
| B2 Markdown | Kimi K2.6 | **0.9065** | 0.4011 | 0.7277 | 0.97 | 0.01 | 3.34 |
| B4 Browser | Kimi K2.6 | 0.8799 | 0.3910 | **0.8379** | 1.00 | 0.02 | 3.15 |
| B3 Vision | Kimi K2.6 | 0.7640 | 0.3003 | 0.8290 | 0.88 | 0.00 | 1.00 |
| B4 Browser | Gemma 4 8B | 0.7392 | 0.2735 | 0.5482 | 0.93 | 0.00 | 3.82 |
| B2 Markdown | Gemma 4 8B | 0.5816 | 0.1940 | 0.5753 | 0.84 | 0.00 | 2.55 |
| B1 HTML | Gemma 4 8B | 0.5324 | 0.1751 | 0.1354 | 0.93 | 0.00 | 3.32 |
| B4 Browser | Qwen2.5-VL 7B | 0.5090 | 0.1463 | 0.4184 | 0.85 | 0.00 | 4.03 |
| B3 Vision | Qwen2.5-VL 7B | 0.5259 | 0.1433 | 0.3985 | 0.76 | 0.00 | 1.72 |
| B2 Markdown | Qwen2.5-VL 7B | 0.4502 | 0.1073 | 0.2700 | 0.65 | 0.00 | 3.06 |
| B1 HTML | Qwen2.5-VL 7B | 0.2447 | 0.0675 | 0.1305 | 0.28 | 0.00 | 6.85 |
| B3 Vision | Gemma 4 8B | 0.0000 | 0.0000 | 0.0410 | 0.05 | 0.00 | 0.36 |

All 1,200 predictions, per-task scores, aggregates and the failure taxonomy are in `results/`.

## Repository layout

```
data/
  splits/                 wadebench_v1_all.jsonl (100 tasks), dev/test split files
  tasks/                  task definitions per domain
  schemas/                JSON schemas (required / recommended / optional fields, normalisation rules, record keys)
  gold/by_task/<domain>/  gold records with normalised values and field-level provenance
  annotation/             per-domain annotation guidelines
  metadata/               site lists, field list, normalisation rules
  processed_evidence/     B4 evidence packages (accessibility tree, text, metadata)
  raw_snapshots/          frozen page bundles (download separately, see below)
  processed_screenshots/  B3 screenshot tiles (download separately, see below)
src/wadebench/            Python package: baselines, evaluator, model clients, utilities, run scripts
prompts/                  prompt templates for the four baselines and annotation
results/                  predictions, per-task scores, aggregates, paper tables
scripts/                  snapshot capture and remediation scripts
docs/                     annotation guidelines and gold-quality audit reports
```

## Getting the snapshots

The frozen page bundles (`page.html`, `page.safe.html`, `text.txt`, `screenshot.png`, `ax_tree.json`, `metadata.json`) and the B3 screenshot tiles are about 1 GB, so they are distributed separately on Hugging Face. **The download link will be added here.** Unzip them into `data/raw_snapshots/` and `data/processed_screenshots/` so the paths in `data/splits/wadebench_v1_all.jsonl` resolve.

Scoring the released predictions does not need the snapshots.

## Quick start

```bash
pip install -r src/wadebench/requirements.txt pandas pydantic pyyaml jsonschema
```

Score one configuration (reproduces the Table 3 row for B2 Markdown + Kimi: record F1 0.9065, strict field F1 0.4011, provenance 0.7277):

```bash
python src/wadebench/scripts/score_predictions.py --pred-dir results/predictions/b2_markdown_llm/kimi-k2_6 --tasks data/splits/wadebench_v1_all.jsonl --schemas-dir data/schemas --output results/scores/b2_markdown_llm__kimi-k2_6.csv
```

Aggregate several score files:

```bash
python src/wadebench/scripts/aggregate_scores.py --scores results/scores/*.csv --output-dir results/aggregate
```

Run a baseline (needs the snapshots; local models need [Ollama](https://ollama.com), Kimi needs `MOONSHOT_API_KEY` in the environment, B4 needs Node.js for `@playwright/mcp`):

```bash
python src/wadebench/scripts/run_baseline.py --baseline b2 --model qwen2.5vl:7b --tasks data/splits/wadebench_v1_all.jsonl --prompt-dir src/wadebench/prompts --num-ctx 131072 --max-chars 200000 --temperature 0
```

Settings used in the paper: `--max-chars` 200000 (Qwen), 400000 (Gemma), 600000 (Kimi); `--max-tiles 24` for B3 (the script default is 8); `--max-evidence-chars 160000` for B4; temperature 0 (local) and 0.6 (Kimi). See `src/wadebench/README_RUNS.md` for more run commands.

## Data, licensing and ethics

- **Code:** MIT License (see `LICENSE`).
- **Annotations and schemas** (gold records, schemas, tasks, guidelines) are released for research use.
- **Snapshots** are copies of publicly accessible web pages captured for research. Their content remains the property of the original website owners. Do not use them for commercial purposes or to republish the sites' content. If you own a captured site and want a page removed, contact us.
- Only public pages were captured; personal data was avoided where possible; capture metadata (URL, date) is kept so sources can be audited.
- Systems evaluated on WADE-Bench should only read the frozen pages and must not perform state-changing actions on live websites.

## Limitations

100 tasks (two per site); one run per configuration (no variance estimates); model configurations differ in input budget, deployment and temperature; record F1 depends on the matching fallback; gold built by one annotator with 100% sequential review by a second (no inter-annotator agreement reported); frozen pages do not test website drift, personalisation or anti-bot behaviour; no DOM-based, wrapper-induction or WebLists baseline yet.

## Citation

```bibtex
@inproceedings{khayoub2026wadebench,
  title     = {{WADE-Bench}: A Schema-Guided Benchmark for Web Data Extraction Agents},
  author    = {Khayoub, Ismail and Chadi, Mohamed-Amine and Mousannif, Hajar and Ait Mohamed, Firdaous},
  booktitle = {Proceedings of the International Conference on Management of Digital EcoSystems (MEDES 2026)},
  year      = {2026}
}
```

## Contact

Ismail Khayoub, LISI Laboratory, Faculty of Sciences Semlalia, Cadi Ayyad University, Marrakech, Morocco. i.khayoub.ced@uca.ac.ma
