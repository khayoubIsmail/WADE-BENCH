from __future__ import annotations

from pathlib import Path
import time
import json

from wadebench.baselines.base import BaseAgent
from wadebench.utils.image_utils import image_to_data_url, create_vertical_tiles
from wadebench.utils.json_utils import extract_json_object, normalize_prediction

from PIL import Image
Image.MAX_IMAGE_PIXELS = None  # allow large real estate screenshots

class VisionLLMBaseline(BaseAgent):
    name = "b3_vision_llm"

    def __init__(
        self,
        model_client,
        schema_loader,
        prompt_path="prompts/b3_vision_llm.txt",
        tile_height: int = 1400,
        overlap: int = 180,
        max_tiles: int = 24,
    ):
        self.model_client = model_client
        self.schema_loader = schema_loader
        self.prompt_template = Path(prompt_path).read_text(encoding="utf-8")
        self.tile_height = tile_height
        self.overlap = overlap
        self.max_tiles = max_tiles

    def build_prompt(self, task: dict, schema: dict, num_tiles: int) -> str:
        task_for_prompt = {
            "task_id": task.get("task_id"),
            "domain": task.get("domain"),
            "task_type": task.get("task_type"),
            "schema_id": task.get("schema_id"),
            "snapshot_path": task.get("snapshot_path"),
            "num_screenshot_tiles": num_tiles,
            "tile_order": "top-to-bottom",
            "provenance_note": "For every field provenance, include source='screenshot.png' and tile_index when known.",
        }
        return (
            self.prompt_template
            .replace("{{TASK_JSON}}", json.dumps(task_for_prompt, indent=2, ensure_ascii=False))
            .replace("{{SCHEMA_JSON}}", json.dumps(schema, indent=2, ensure_ascii=False))
        )

    def get_screenshot_path(self, task: dict) -> str:
        source_files = task.get("source_files", {})
        for key in ["screenshot", "screenshot_png", "screenshot_path"]:
            if key in source_files and source_files[key]:
                return source_files[key]
        raise KeyError(f"No screenshot path found in source_files for task {task.get('task_id')}")

    def _repair_json_once(self, bad_output: str):
        repair_prompt = (
            "The previous output was invalid JSON. Return only one valid JSON object with a records list. "
            "Keep every valid extracted record and preserve field-level screenshot provenance where possible. "
            "No markdown. No explanation. First character must be { and last character must be }.\n\n"
            f"Invalid output:\n{bad_output[:16000]}"
        )
        response = self.model_client.complete(prompt=repair_prompt)
        payload = normalize_prediction(extract_json_object(response.text))
        return payload, response

    def run_task(self, task: dict) -> dict:
        start = time.time()
        task_id = task["task_id"]
        domain = task.get("domain")
        schema_id = task["schema_id"]
        try:
            schema = self.schema_loader.load_schema(schema_id)
            screenshot_path = self.get_screenshot_path(task)
            tile_dir = Path("data/processed_screenshots/b3_tiles") / task_id
            tile_paths = create_vertical_tiles(
                image_path=screenshot_path,
                output_dir=tile_dir,
                tile_height=self.tile_height,
                overlap=self.overlap,
                max_tiles=self.max_tiles,
            )
            image_data_urls = [image_to_data_url(p) for p in tile_paths]
            prompt = self.build_prompt(task, schema, num_tiles=len(tile_paths))
            initial_response = self.model_client.complete_with_images(prompt=prompt, image_data_urls=image_data_urls)

            repaired = False
            repair_response = None
            try:
                payload = normalize_prediction(extract_json_object(initial_response.text))
                success = True
                error = None
            except Exception as parse_error:
                try:
                    payload, repair_response = self._repair_json_once(initial_response.text)
                    repaired = True
                    success = True
                    error = f"json_repaired_after_error: {parse_error}"
                except Exception as repair_error:
                    payload = {"records": []}
                    success = False
                    error = f"json_parse_failed: {parse_error} | repair_failed: {repair_error}"

            input_tokens = getattr(initial_response, "input_tokens", 0) + (getattr(repair_response, "input_tokens", 0) if repair_response else 0)
            output_tokens = getattr(initial_response, "output_tokens", 0) + (getattr(repair_response, "output_tokens", 0) if repair_response else 0)
            total_tokens = getattr(initial_response, "total_tokens", 0) + (getattr(repair_response, "total_tokens", 0) if repair_response else 0)

            return {
                "task_id": task_id,
                "baseline": self.name,
                "model": self.model_client.model_name,
                "domain": domain,
                "schema_id": schema_id,
                "records": payload.get("records", []),
                "run_metadata": {
                    "success": success,
                    "json_valid": success,
                    "runtime_success": success,
                    "repaired": repaired,
                    "latency_seconds": round(time.time() - start, 3),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "num_tiles": len(tile_paths),
                    "tile_height": self.tile_height,
                    "tile_overlap": self.overlap,
                    "max_tiles": self.max_tiles,
                    "tile_paths": [str(p) for p in tile_paths],
                    "error": error,
                },
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "baseline": self.name,
                "model": getattr(self.model_client, "model_name", "unknown"),
                "domain": domain,
                "schema_id": schema_id,
                "records": [],
                "run_metadata": {
                    "success": False,
                    "json_valid": False,
                    "runtime_success": False,
                    "latency_seconds": round(time.time() - start, 3),
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "num_tiles": 0,
                    "error": str(e),
                },
            }
