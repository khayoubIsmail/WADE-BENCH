from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wadebench.io.output_writer import OutputWriter, safe_model_slug
from wadebench.utils.json_utils import extract_json_object, normalize_prediction


def extract_response_text(item: dict, partial_json: bool) -> tuple[str, dict, str | None]:
    err = item.get("error")
    if err:
        return "", {}, str(err)
    response = item.get("response") or {}
    status_code = response.get("status_code") or response.get("status")
    body = response.get("body") or item.get("body") or {}
    if status_code and int(status_code) >= 400:
        return "", body, f"http_status_{status_code}: {body}"
    try:
        text = body["choices"][0]["message"].get("content") or ""
    except Exception:
        text = ""
    if partial_json:
        text = "{" + text
    return text, body, None


def usage_from_body(body: dict) -> tuple[int, int, int]:
    usage = body.get("usage") or {}
    prompt = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    completion = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    total = int(usage.get("total_tokens") or (prompt + completion))
    return prompt, completion, total


def main():
    parser = argparse.ArgumentParser(description="Convert Kimi Batch output JSONL files into WADE-Bench prediction JSON files.")
    parser.add_argument("--manifest", required=True, help="results/kimi_batch/<baseline>/batch_manifest.json")
    parser.add_argument("--outputs-dir", required=True, help="results/kimi_batch/<baseline>/outputs")
    parser.add_argument("--output-root", default="results/predictions")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    reqs = manifest.get("requests", {})
    baseline = manifest["baseline"]
    model_slug = safe_model_slug("kimi-k2.6")
    out_dir = Path(args.output_root) / baseline / model_slug
    writer = OutputWriter(str(out_dir))

    ok = 0
    failed = 0
    seen = set()

    for path in sorted(Path(args.outputs_dir).glob("*_output.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            custom_id = item.get("custom_id")
            meta = reqs.get(custom_id)
            if not meta:
                print(f"WARNING: unknown custom_id {custom_id}")
                continue
            seen.add(custom_id)
            task_id = meta["task_id"]
            text, body, api_error = extract_response_text(item, manifest.get("partial_json", False))
            prompt_tokens, completion_tokens, total_tokens = usage_from_body(body)
            try:
                if api_error:
                    raise ValueError(api_error)
                payload = normalize_prediction(extract_json_object(text))
                success = True
                error = None
                records = payload.get("records", [])
                ok += 1
            except Exception as e:
                success = False
                error = str(e)
                records = []
                failed += 1

            pred = {
                "task_id": task_id,
                "baseline": baseline,
                "model": "kimi-k2.6",
                "domain": meta.get("domain"),
                "schema_id": meta.get("schema_id"),
                "records": records,
                "run_metadata": {
                    "success": success,
                    "json_valid": success,
                    "runtime_success": success,
                    "latency_seconds": None,
                    "input_tokens": prompt_tokens,
                    "output_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "batch": True,
                    "prompt_cache": manifest.get("prompt_cache", False),
                    "partial_json": manifest.get("partial_json", False),
                    "custom_id": custom_id,
                    "imported_at": int(time.time()),
                    "error": error,
                    **(meta.get("metadata") or {}),
                },
            }
            writer.write_prediction(pred)

    missing = set(reqs) - seen
    for custom_id in sorted(missing):
        meta = reqs[custom_id]
        pred = {
            "task_id": meta["task_id"],
            "baseline": baseline,
            "model": "kimi-k2.6",
            "domain": meta.get("domain"),
            "schema_id": meta.get("schema_id"),
            "records": [],
            "run_metadata": {
                "success": False,
                "json_valid": False,
                "runtime_success": False,
                "latency_seconds": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "batch": True,
                "prompt_cache": manifest.get("prompt_cache", False),
                "partial_json": manifest.get("partial_json", False),
                "custom_id": custom_id,
                "error": "missing_from_batch_output",
            },
        }
        writer.write_prediction(pred)
        failed += 1

    print(json.dumps({"done": True, "output_dir": str(out_dir), "ok": ok, "failed": failed, "missing": len(missing)}, indent=2))


if __name__ == "__main__":
    main()
