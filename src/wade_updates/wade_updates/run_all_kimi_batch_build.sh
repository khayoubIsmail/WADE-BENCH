#!/bin/bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH=.

TASKS=${TASKS:-data/splits/wadebench_v1_all.jsonl}
SCHEMAS=${SCHEMAS:-data/schemas}
OUT=${OUT:-results/kimi_batch}
MAX_TILES=${MAX_TILES:-16}
MAX_CHARS=${MAX_CHARS:-0}
MAX_EVIDENCE_CHARS=${MAX_EVIDENCE_CHARS:-160000}
MAX_TOKENS=${MAX_TOKENS:-8192}

python scripts/build_kimi_batch.py --baseline b1 --tasks "$TASKS" --schemas-dir "$SCHEMAS" --output-dir "$OUT" --max-chars "$MAX_CHARS" --max-tokens "$MAX_TOKENS"
python scripts/build_kimi_batch.py --baseline b2 --tasks "$TASKS" --schemas-dir "$SCHEMAS" --output-dir "$OUT" --max-chars "$MAX_CHARS" --max-tokens "$MAX_TOKENS"
python scripts/build_kimi_batch.py --baseline b3 --tasks "$TASKS" --schemas-dir "$SCHEMAS" --output-dir "$OUT" --max-tiles "$MAX_TILES" --max-tokens "$MAX_TOKENS"
python scripts/build_kimi_batch.py --baseline b4 --tasks "$TASKS" --schemas-dir "$SCHEMAS" --output-dir "$OUT" --max-evidence-chars "$MAX_EVIDENCE_CHARS" --max-tokens "$MAX_TOKENS"

echo "Built Kimi batch request files under $OUT"
