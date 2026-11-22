#!/bin/bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH=.

OUT=${OUT:-results/kimi_batch}
WINDOW=${WINDOW:-24h}

for manifest in "$OUT"/*/batch_manifest.json; do
  echo "Submitting $manifest"
  python scripts/submit_kimi_batch.py --manifest "$manifest" --completion-window "$WINDOW"
done

echo "Submitted Kimi batch jobs. Use run_all_kimi_batch_check.sh to poll/download."
