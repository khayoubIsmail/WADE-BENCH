#!/bin/bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH=.

OUT=${OUT:-results/kimi_batch}
PRED=${PRED:-results/predictions}

for manifest in "$OUT"/*/batch_manifest.json; do
  base_dir=$(dirname "$manifest")
  if [ -d "$base_dir/outputs" ]; then
    echo "Importing $base_dir"
    python scripts/import_kimi_batch_results.py --manifest "$manifest" --outputs-dir "$base_dir/outputs" --output-root "$PRED"
  else
    echo "Skipping $base_dir: outputs folder not found"
  fi
done

echo "Imported Kimi batch results into $PRED"
