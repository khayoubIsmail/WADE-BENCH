from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from repository root without installation.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wadebench.io.task_loader import TaskLoader
from wadebench.io.schema_loader import SchemaLoader
from wadebench.io.output_writer import OutputWriter, safe_model_slug
from wadebench.models.model_client import create_model_client
from wadebench.baselines.b1_html_llm import HTMLLLMBaseline
from wadebench.baselines.b2_markdown_llm import MarkdownLLMBaseline
from wadebench.baselines.b3_vision_llm import VisionLLMBaseline
from wadebench.baselines.b4_playwright_mcp_agent import PlaywrightMCPAgentBaseline


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


def build_baseline(args, model_client, schema_loader):
    baseline = BASELINE_ALIASES[args.baseline]
    prompt_dir = Path(args.prompt_dir)
    if baseline == "b1_html_llm":
        return HTMLLLMBaseline(
            model_client=model_client,
            schema_loader=schema_loader,
            prompt_path=prompt_dir / "b1_html_llm.txt",
            max_chars=args.max_chars,
        )
    if baseline == "b2_markdown_llm":
        return MarkdownLLMBaseline(
            model_client=model_client,
            schema_loader=schema_loader,
            prompt_path=prompt_dir / "b2_markdown_llm.txt",
            max_chars=args.max_chars,
        )
    if baseline == "b3_vision_llm":
        return VisionLLMBaseline(
            model_client=model_client,
            schema_loader=schema_loader,
            prompt_path=prompt_dir / "b3_vision_llm.txt",
            tile_height=args.tile_height,
            overlap=args.tile_overlap,
            max_tiles=args.max_tiles,
        )
    if baseline == "b4_playwright_mcp_agent":
        return PlaywrightMCPAgentBaseline(
            model_client=model_client,
            schema_loader=schema_loader,
            prompt_path=prompt_dir / "b4_playwright_mcp_agent.txt",
            split=args.split,
            max_evidence_chars=args.max_evidence_chars,
        )
    raise ValueError(f"Unsupported baseline: {args.baseline}")


def main():
    parser = argparse.ArgumentParser(description="Run one WADE-Bench baseline with one LLM.")
    parser.add_argument("--baseline", required=True, choices=sorted(BASELINE_ALIASES.keys()))
    parser.add_argument("--model", required=True, help="gemma4:e4b, qwen3-vl:8b, kimi-k2.6, etc.")
    parser.add_argument("--tasks", required=True, help="JSONL task split file")
    parser.add_argument("--schemas-dir", default="data/schemas")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--output-root", default="results/predictions")
    parser.add_argument("--split", default="dev")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--num-ctx", type=int, default=None, help="Ollama runtime num_ctx, e.g. 131072")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max output tokens (default: no limit)")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-chars", type=int, default=400000, help="B1/B2 prompt input truncation")
    parser.add_argument("--max-evidence-chars", type=int, default=160000, help="B4 evidence truncation")
    parser.add_argument("--tile-height", type=int, default=1400)
    parser.add_argument("--tile-overlap", type=int, default=180)
    parser.add_argument("--max-tiles", type=int, default=8)
    args = parser.parse_args()

    baseline_name = BASELINE_ALIASES[args.baseline]
    model_slug = safe_model_slug(args.model)
    out_dir = Path(args.output_root) / baseline_name / model_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    model_client = create_model_client(
        args.model,
        num_ctx=args.num_ctx,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )
    schema_loader = SchemaLoader(args.schemas_dir)
    baseline = build_baseline(args, model_client, schema_loader)
    writer = OutputWriter(str(out_dir))

    tasks = TaskLoader(args.tasks).load_all_tasks()
    if args.limit:
        tasks = tasks[: args.limit]

    run_manifest = {
        "baseline": baseline_name,
        "model": model_client.model_name,
        "requested_model": args.model,
        "num_ctx": args.num_ctx,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "tasks_file": args.tasks,
        "schemas_dir": args.schemas_dir,
        "output_dir": str(out_dir),
        "num_tasks_planned": len(tasks),
    }
    (out_dir / "_run_manifest.json").write_text(json.dumps(run_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    ok = 0
    failed = 0
    for i, task in enumerate(tasks, start=1):
        task_id = task.get("task_id", f"task_{i}")
        target_path = out_dir / f"{task_id}.json"
        if args.skip_existing and target_path.exists():
            print(f"[{i}/{len(tasks)}] SKIP {task_id}")
            continue
        print(f"[{i}/{len(tasks)}] RUN {baseline_name} | {model_client.model_name} | {task_id}", flush=True)
        pred = baseline.run_task(task)
        writer.write_prediction(pred)
        if pred.get("run_metadata", {}).get("success"):
            ok += 1
        else:
            failed += 1
            print(f"    ERROR: {pred.get('run_metadata', {}).get('error')}", flush=True)

    print(json.dumps({"done": True, "output_dir": str(out_dir), "ok": ok, "failed": failed}, indent=2))


if __name__ == "__main__":
    main()
