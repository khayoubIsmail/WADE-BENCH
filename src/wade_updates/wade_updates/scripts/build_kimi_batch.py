from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wadebench.io.task_loader import TaskLoader
from wadebench.io.schema_loader import SchemaLoader
from wadebench.io.output_writer import safe_model_slug
from wadebench.baselines.b1_html_llm import HTMLLLMBaseline
from wadebench.baselines.b2_markdown_llm import MarkdownLLMBaseline
from wadebench.baselines.b3_vision_llm import VisionLLMBaseline
from wadebench.baselines.b4_playwright_mcp_agent import PlaywrightMCPAgentBaseline
from wadebench.utils.html_utils import read_html, lightly_clean_html, truncate_html
from wadebench.utils.html_to_markdown import html_file_to_markdown
from wadebench.utils.image_utils import create_vertical_tiles, image_to_data_url
from wadebench.utils.mcp_snapshot_evidence import build_b4_mcp_evidence, save_b4_evidence_and_trace

BASELINE_ALIASES = {
    "b1": "b1_html_llm",
    "b1_html_llm": "b1_html_llm",
    "b2": "b2_markdown_llm",
    "b2_markdown_llm": "b2_markdown_llm",
    "b3": "b3_vision_llm",
    "b3_vision_llm": "b3_vision_llm",
    "b4": "b4_playwright_mcp_agent",
    "b4_playwright_mcp_agent": "b4_playwright_mcp_agent",
}

TEXT_SYSTEM = (
    "You are a precise web data extraction engine. Return valid JSON only. "
    "No markdown. No explanation. No comments. The first character must be { "
    "and the last character must be }."
)
VISION_SYSTEM = (
    "You are a precise visual web data extraction engine. Use only the provided "
    "screenshot tiles. Return valid JSON only. No markdown. No explanation. "
    "The first character must be { and the last character must be }."
)


class DummyModel:
    model_name = "kimi-k2.6"


def make_baseline(args, schema_loader):
    baseline = BASELINE_ALIASES[args.baseline]
    prompt_dir = Path(args.prompt_dir)
    dummy = DummyModel()
    if baseline == "b1_html_llm":
        return HTMLLLMBaseline(dummy, schema_loader, prompt_dir / "b1_html_llm.txt", max_chars=args.max_chars)
    if baseline == "b2_markdown_llm":
        return MarkdownLLMBaseline(dummy, schema_loader, prompt_dir / "b2_markdown_llm.txt", max_chars=args.max_chars)
    if baseline == "b3_vision_llm":
        return VisionLLMBaseline(dummy, schema_loader, prompt_dir / "b3_vision_llm.txt", tile_height=args.tile_height, overlap=args.tile_overlap, max_tiles=args.max_tiles)
    if baseline == "b4_playwright_mcp_agent":
        return PlaywrightMCPAgentBaseline(dummy, schema_loader, prompt_dir / "b4_playwright_mcp_agent.txt", split=args.split, max_evidence_chars=args.max_evidence_chars)
    raise ValueError(f"Unknown baseline: {args.baseline}")


def build_messages_for_task(args, baseline_obj, baseline_name: str, task: dict, schema: dict) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return (messages, extra_metadata). Does not call the model."""
    task_id = task["task_id"]

    if baseline_name == "b1_html_llm":
        page_html = task["source_files"].get("page_html") or task["source_files"].get("html")
        if not page_html:
            raise KeyError("source_files.page_html missing")
        html = truncate_html(lightly_clean_html(read_html(page_html)), max_chars=args.max_chars)
        prompt = baseline_obj.build_prompt(task, schema, html)
        messages = [{"role": "system", "content": TEXT_SYSTEM}, {"role": "user", "content": prompt}]
        return messages, {"input_kind": "html", "source_file": page_html}

    if baseline_name == "b2_markdown_llm":
        page_html = task["source_files"].get("page_html") or task["source_files"].get("html")
        if not page_html:
            raise KeyError("source_files.page_html missing")
        markdown = html_file_to_markdown(page_html, max_chars=args.max_chars)
        prompt = baseline_obj.build_prompt(task, schema, markdown)
        messages = [{"role": "system", "content": TEXT_SYSTEM}, {"role": "user", "content": prompt}]
        return messages, {"input_kind": "markdown", "source_file": page_html}

    if baseline_name == "b3_vision_llm":
        screenshot_path = baseline_obj.get_screenshot_path(task)
        tile_dir = Path(args.tile_output_dir) / task_id
        tile_paths = create_vertical_tiles(
            image_path=screenshot_path,
            output_dir=tile_dir,
            tile_height=args.tile_height,
            overlap=args.tile_overlap,
            max_tiles=args.max_tiles,
        )
        prompt = baseline_obj.build_prompt(task, schema, num_tiles=len(tile_paths))
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for idx, tile_path in enumerate(tile_paths, start=1):
            content.append({"type": "text", "text": f"Screenshot tile {idx}, ordered from top to bottom:"})
            content.append({"type": "image_url", "image_url": {"url": image_to_data_url(tile_path)}})
        messages = [{"role": "system", "content": VISION_SYSTEM}, {"role": "user", "content": content}]
        return messages, {
            "input_kind": "vision_tiles",
            "screenshot_path": str(screenshot_path),
            "num_tiles": len(tile_paths),
            "tile_height": args.tile_height,
            "tile_overlap": args.tile_overlap,
            "max_tiles": args.max_tiles,
            "tile_paths": [str(p) for p in tile_paths],
        }

    if baseline_name == "b4_playwright_mcp_agent":
        evidence = build_b4_mcp_evidence(task)
        evidence_path, trace_path = save_b4_evidence_and_trace(evidence=evidence, task_id=task_id, split=args.split)
        prompt = baseline_obj.build_prompt(task, schema, evidence)
        messages = [{"role": "system", "content": TEXT_SYSTEM}, {"role": "user", "content": prompt}]
        return messages, {"input_kind": "frozen_snapshot_evidence", "evidence_path": evidence_path, "tool_trace_path": trace_path}

    raise ValueError(f"Unsupported baseline: {baseline_name}")


def request_body(args, baseline_name: str, task: dict, messages: list[dict[str, Any]]) -> dict[str, Any]:
    schema_id = task.get("schema_id", "schema")
    body: dict[str, Any] = {
        "model": "kimi-k2.6",
        "messages": messages,
        "max_tokens": args.max_tokens,
        "thinking": {"type": "disabled"},
    }

    # Batch API docs say do NOT include temperature/top_p/n/presence_penalty/frequency_penalty for kimi-k2.6.
    # Prompt cache key is safe: it only optimizes cache-hit routing; it does not change evidence or scoring.
    if not args.no_prompt_cache:
        safe_schema = str(schema_id).replace(" ", "_")
        body["prompt_cache_key"] = f"{args.prompt_cache_prefix}:{baseline_name}:{safe_schema}:v1"

    # Kimi Partial Mode strongly improves JSON-format compliance. The returned content omits this prefix,
    # and import_kimi_batch_results.py prepends it before JSON parsing.
    if args.partial_json:
        body["messages"] = list(messages) + [{"role": "assistant", "content": "{", "partial": True}]

    return body


def write_chunks(lines: list[str], out_dir: Path, max_file_mb: int) -> list[Path]:
    max_bytes = max_file_mb * 1024 * 1024
    out_paths: list[Path] = []
    part = 1
    current: list[str] = []
    current_bytes = 0

    def flush():
        nonlocal part, current, current_bytes
        if not current:
            return
        path = out_dir / f"requests_part{part:03d}.jsonl"
        path.write_text("".join(current), encoding="utf-8")
        out_paths.append(path)
        part += 1
        current = []
        current_bytes = 0

    for line in lines:
        b = len(line.encode("utf-8"))
        if current and current_bytes + b > max_bytes:
            flush()
        current.append(line)
        current_bytes += b
        if b > max_bytes:
            print(f"WARNING: a single request is larger than {max_file_mb} MB; Kimi may reject that batch file.")
            flush()
    flush()
    return out_paths


def main():
    parser = argparse.ArgumentParser(description="Build Kimi Batch API JSONL requests for one WADE-Bench baseline.")
    parser.add_argument("--baseline", required=True, choices=sorted(BASELINE_ALIASES.keys()))
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--schemas-dir", default="data/schemas")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--output-dir", default="results/kimi_batch")
    parser.add_argument("--split", default="dev")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-chars", type=int, default=0, help="Max chars for B1/B2 text inputs. 0 disables truncation (recommended for Kimi K2.6).")
    parser.add_argument("--max-evidence-chars", type=int, default=160000)
    parser.add_argument("--tile-height", type=int, default=1400)
    parser.add_argument("--tile-overlap", type=int, default=180)
    parser.add_argument("--max-tiles", type=int, default=16)
    parser.add_argument("--tile-output-dir", default="data/processed_screenshots/kimi_batch_tiles")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--max-file-mb", type=int, default=90, help="Kimi file limit is 100MB; use 90MB margin.")
    parser.add_argument("--prompt-cache-prefix", default="wadebench-v1-kimi")
    parser.add_argument("--no-prompt-cache", action="store_true")
    parser.add_argument("--no-partial-json", dest="partial_json", action="store_false", default=True)
    args = parser.parse_args()
    # For Kimi K2.6, do not truncate B1/B2 by default.
    # Use --max-chars N only for debugging or if a request exceeds provider/file limits.
    if args.max_chars is not None and args.max_chars <= 0:
        args.max_chars = None

    baseline_name = BASELINE_ALIASES[args.baseline]
    out_dir = Path(args.output_dir) / baseline_name
    out_dir.mkdir(parents=True, exist_ok=True)

    schema_loader = SchemaLoader(args.schemas_dir)
    baseline_obj = make_baseline(args, schema_loader)
    tasks = TaskLoader(args.tasks).load_all_tasks()
    if args.limit:
        tasks = tasks[: args.limit]

    lines: list[str] = []
    manifest: dict[str, Any] = {
        "model": "kimi-k2.6",
        "baseline": baseline_name,
        "tasks_file": args.tasks,
        "schemas_dir": args.schemas_dir,
        "partial_json": args.partial_json,
        "prompt_cache": not args.no_prompt_cache,
        "requests": {},
    }

    failures = []
    for i, task in enumerate(tasks, start=1):
        task_id = task.get("task_id", f"task_{i}")
        custom_id = f"{baseline_name}::{task_id}"
        try:
            schema = schema_loader.load_schema(task["schema_id"])
            messages, meta = build_messages_for_task(args, baseline_obj, baseline_name, task, schema)
            body = request_body(args, baseline_name, task, messages)
            req = {"custom_id": custom_id, "method": "POST", "url": "/v1/chat/completions", "body": body}
            lines.append(json.dumps(req, ensure_ascii=False) + "\n")
            manifest["requests"][custom_id] = {
                "task_id": task_id,
                "baseline": baseline_name,
                "model": "kimi-k2.6",
                "domain": task.get("domain"),
                "schema_id": task.get("schema_id"),
                "metadata": meta,
            }
            print(f"[{i}/{len(tasks)}] BUILT {custom_id}")
        except Exception as e:
            failures.append({"task_id": task_id, "error": str(e)})
            print(f"[{i}/{len(tasks)}] ERROR {task_id}: {e}")

    paths = write_chunks(lines, out_dir, args.max_file_mb)
    manifest["batch_request_files"] = [str(p) for p in paths]
    manifest["build_failures"] = failures
    manifest_path = out_dir / "batch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"done": True, "baseline": baseline_name, "requests": len(lines), "failures": len(failures), "files": [str(p) for p in paths], "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
