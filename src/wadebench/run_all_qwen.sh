#!/bin/bash
set -e

cd "$(dirname "$0")/../.."
export PYTHONPATH=src

TASKS=data/splits/wadebench_v1_all.jsonl
MODEL=qwen2.5vl:7b
SCHEMAS=data/schemas

python src/wadebench/scripts/run_baseline.py --baseline b1 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --num-ctx 131072 --max-chars 200000

python src/wadebench/scripts/run_baseline.py --baseline b2 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --num-ctx 131072 --max-chars 200000

python src/wadebench/scripts/run_baseline.py --baseline b3 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --num-ctx 131072 --max-tiles 24

python src/wadebench/scripts/run_baseline.py --baseline b4 --model $MODEL --tasks $TASKS --schemas-dir $SCHEMAS --output-root results/predictions --num-ctx 131072 --max-evidence-chars 160000

echo "Qwen2.5-VL done."
