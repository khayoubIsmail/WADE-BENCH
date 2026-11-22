#!/bin/bash
set -e

cd "$(dirname "$0")/../.."
export PYTHONPATH=src

TASKS=data/splits/wadebench_v1_all.jsonl
MODEL=kimi-k2.6
SCHEMAS=data/schemas

python src/wadebench/scripts/run_baseline.py --baseline b1 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --max-chars 600000

python src/wadebench/scripts/run_baseline.py --baseline b2 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --max-chars 600000

python src/wadebench/scripts/run_baseline.py --baseline b3 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --max-tiles 24 --max-chars 600000

python src/wadebench/scripts/run_baseline.py --baseline b4 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --max-evidence-chars 160000 --max-chars 600000

echo "Kimi done."
