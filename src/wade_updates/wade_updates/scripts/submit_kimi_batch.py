from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def api_key() -> str:
    key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_API_KEY")
    if not key:
        raise SystemExit("Missing MOONSHOT_API_KEY or KIMI_API_KEY in environment/.env")
    return key


def post_upload(path: Path, key: str, base_url: str) -> dict:
    with path.open("rb") as f:
        r = requests.post(
            f"{base_url}/files",
            headers={"Authorization": f"Bearer {key}"},
            data={"purpose": "batch"},
            files={"file": (path.name, f, "application/jsonl")},
            timeout=300,
        )
    r.raise_for_status()
    return r.json()


def create_batch(file_id: str, key: str, base_url: str, completion_window: str, metadata: dict) -> dict:
    r = requests.post(
        f"{base_url}/batches",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"input_file_id": file_id, "endpoint": "/v1/chat/completions", "completion_window": completion_window, "metadata": metadata},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Upload Kimi batch request files and create batch jobs.")
    parser.add_argument("--manifest", required=True, help="results/kimi_batch/<baseline>/batch_manifest.json")
    parser.add_argument("--completion-window", default="24h", help="Kimi supports 12h to 7d, e.g. 12h, 24h, 1d")
    parser.add_argument("--base-url", default="https://api.moonshot.ai/v1")
    args = parser.parse_args()

    key = api_key()
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    jobs = []
    for i, file_path_str in enumerate(manifest.get("batch_request_files", []), start=1):
        file_path = Path(file_path_str)
        print(f"UPLOAD {file_path}")
        uploaded = post_upload(file_path, key, args.base_url)
        print(f"CREATE BATCH for file_id={uploaded['id']}")
        batch = create_batch(
            uploaded["id"],
            key,
            args.base_url,
            args.completion_window,
            metadata={"baseline": manifest.get("baseline", ""), "part": str(i)},
        )
        jobs.append({"request_file": str(file_path), "uploaded_file": uploaded, "batch": batch})

    out = manifest_path.parent / "batch_jobs.json"
    out.write_text(json.dumps({"jobs": jobs}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"done": True, "jobs_file": str(out), "num_jobs": len(jobs)}, indent=2))


if __name__ == "__main__":
    main()
