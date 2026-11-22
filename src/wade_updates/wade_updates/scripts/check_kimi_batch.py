from __future__ import annotations

import argparse
import json
import os
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


def get_json(url: str, key: str) -> dict:
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=120)
    r.raise_for_status()
    return r.json()


def get_text(url: str, key: str) -> str:
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=300)
    r.raise_for_status()
    return r.text


def main():
    parser = argparse.ArgumentParser(description="Check Kimi batch status and download completed outputs.")
    parser.add_argument("--jobs", required=True, help="results/kimi_batch/<baseline>/batch_jobs.json")
    parser.add_argument("--base-url", default="https://api.moonshot.ai/v1")
    args = parser.parse_args()

    key = api_key()
    jobs_path = Path(args.jobs)
    data = json.loads(jobs_path.read_text(encoding="utf-8"))
    output_dir = jobs_path.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    statuses = []
    for j in data.get("jobs", []):
        batch_id = j["batch"]["id"]
        status = get_json(f"{args.base_url}/batches/{batch_id}", key)
        statuses.append(status)
        print(f"{batch_id}: {status.get('status')} {status.get('request_counts')}")
        if status.get("status") == "completed":
            if status.get("output_file_id"):
                text = get_text(f"{args.base_url}/files/{status['output_file_id']}/content", key)
                (output_dir / f"{batch_id}_output.jsonl").write_text(text, encoding="utf-8")
            if status.get("error_file_id"):
                text = get_text(f"{args.base_url}/files/{status['error_file_id']}/content", key)
                (output_dir / f"{batch_id}_errors.jsonl").write_text(text, encoding="utf-8")

    out = jobs_path.parent / "batch_status.json"
    out.write_text(json.dumps(statuses, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"done": True, "status_file": str(out), "outputs_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
