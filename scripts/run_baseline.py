import sys
import os
import json
import argparse
from pathlib import Path

# Add src directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from wadebench.io.task_loader import TaskLoader
from wadebench.io.schema_loader import SchemaLoader
from wadebench.models.model_client import create_model_client
from wadebench.baselines.b1_html_llm import HTMLLLMBaseline
from wadebench.baselines.b2_markdown_llm import MarkdownLLMBaseline
from wadebench.baselines.b3_vision_llm import VisionLLMBaseline
from wadebench.baselines.b4_playwright_mcp_agent import PlaywrightMCPAgentBaseline

SPLIT_FILES = {
    "dev": "data/splits/wadebench_v1_3domain_dev.jsonl",
    "test": "data/splits/wadebench_v1_3domain_test.jsonl",
    "all": "data/splits/wadebench_v1_3domain_all.jsonl",
}

def main():
    parser = argparse.ArgumentParser(description="WADE-Bench Baseline Runner")
    parser.add_argument("--baseline", required=True, help="Baseline name (e.g. b1_html_llm)")
    parser.add_argument("--model", required=True, help="Model name (e.g. claude_haiku, gpt-4o)")
    parser.add_argument("--split", required=True, help="Split shortcut (dev, test, all) or path to jsonl")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tasks to run")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing results")
    args = parser.parse_args()

    # 1. Parse split file
    if args.split in SPLIT_FILES:
        split_file = SPLIT_FILES[args.split]
    else:
        split_file = args.split

    # 2. Setup output dir
    output_dir = PROJECT_ROOT / "results" / args.baseline / args.model / Path(args.split).stem
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Load tasks
    loader = TaskLoader(split_file)
    tasks = loader.load_all_tasks()
    if args.limit:
        tasks = tasks[:args.limit]

    print(f"Loaded {len(tasks)} tasks from {split_file}")
    print(f"Output directory: {output_dir}")

    # 4. Initialize components
    model_client = create_model_client(args.model)
    schema_loader = SchemaLoader(str(PROJECT_ROOT / "data" / "schemas"))

    if args.baseline == "b1_html_llm":
        agent = HTMLLLMBaseline(model_client=model_client, schema_loader=schema_loader)
    elif args.baseline == "b2_markdown_llm":
        agent = MarkdownLLMBaseline(model_client=model_client, schema_loader=schema_loader)
    elif args.baseline == "b3_vision_llm":
        agent = VisionLLMBaseline(model_client=model_client, schema_loader=schema_loader)
    elif args.baseline == "b4_playwright_mcp_agent":
        agent = PlaywrightMCPAgentBaseline(
            model_client=model_client,
            schema_loader=schema_loader,
            split=args.split,
        )
    else:
        print(f"Unknown baseline: {args.baseline}")
        sys.exit(1)

    # 5. Run tasks
    for i, task in enumerate(tasks):
        task_id = task["task_id"]
        out_path = output_dir / f"{task_id}.json"
        
        print(f"[{i+1}/{len(tasks)}] Running {task_id}...")

        if out_path.exists() and not args.overwrite:
            print(f"  Skipping {task_id} (already exists)")
            continue

        try:
            result = agent.run_task(task)
            
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if result["run_metadata"]["success"]:
                print(f"  Success ({result['run_metadata']['latency_seconds']}s, {result['run_metadata']['output_tokens']} tokens)")
            else:
                print(f"  Failed: {result['run_metadata']['error']}")
        except Exception as e:
            print(f"  Crash: {str(e)}")

if __name__ == "__main__":
    main()
