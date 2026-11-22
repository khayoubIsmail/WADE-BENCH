#!/bin/bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH=.

OUT=${OUT:-results/kimi_batch}

for jobs in "$OUT"/*/batch_jobs.json; do
  echo "Checking $jobs"
  python scripts/check_kimi_batch.py --jobs "$jobs"
done

echo "If all jobs are completed, run run_all_kimi_batch_import.sh"
