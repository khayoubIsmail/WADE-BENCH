from __future__ import annotations

from pathlib import Path
import time
import json

from wadebench.baselines.base import BaseAgent
from wadebench.utils.html_utils import read_html, lightly_clean_html, truncate_html
from wadebench.utils.json_utils import extract_json_object, normalize_prediction


class HTMLLLMBaseline(BaseAgent):
    name = "b1_html_llm"

    def __init__(self, model_client, schema_loader, prompt_path="prompts/b1_html_llm.txt", max_chars: int | None = None):
        self.model_client = model_client
        self.schema_loader = schema_loader
        self.prompt_template = Path(prompt_path).read_text(encoding="utf-8")
        self.max_chars = max_chars

    def build_prompt(self, task: dict, schema: dict, html: str) -> str:
        task_for_prompt = {
            "task_id": task.get("task_id"),
            "domain": task.get("domain"),
            "task_type": task.get("task_type"),
            "schema_id": task.get("schema_id"),
            "snapshot_path": task.get("snapshot_path"),
        }
        return (
            self.prompt_template
            .replace("{{TASK_JSON}}", json.dumps(task_for_prompt, indent=2, ensure_ascii=False))
            .replace("{{SCHEMA_JSON}}", json.dumps(schema, indent=2, ensure_ascii=False))
            .replace("{{HTML_CONTENT}}", html)
        )

    def _repair_json_once(self, bad_output: str):
        repair_prompt = (
            "The previous output was invalid JSON. Return only one valid JSON object with a records list. "
            "Keep every valid extracted record and preserve field-level provenance where possible. "
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
            page_html = task["source_files"].get("page_html") or task["source_files"].get("html")
            if not page_html:
                raise KeyError("source_files.page_html missing")
            html = truncate_html(lightly_clean_html(read_html(page_html)), max_chars=self.max_chars)
            prompt = self.build_prompt(task, schema, html)
            initial_response = self.model_client.complete(prompt=prompt)

            repaired = False
            repair_response = None
            try:
                payload = normalize_prediction(extract_json_object(initial_response.text))
                error = None
            except Exception as parse_error:
                payload, repair_response = self._repair_json_once(initial_response.text)
                repaired = True
                error = f"json_repaired_after_error: {parse_error}"

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
                    "success": True,
                    "json_valid": True,
                    "runtime_success": True,
                    "latency_seconds": round(time.time() - start, 3),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "initial_input_tokens": getattr(initial_response, "input_tokens", 0),
                    "initial_output_tokens": getattr(initial_response, "output_tokens", 0),
                    "repair_input_tokens": getattr(repair_response, "input_tokens", 0) if repair_response else 0,
                    "repair_output_tokens": getattr(repair_response, "output_tokens", 0) if repair_response else 0,
                    "repaired": repaired,
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
                    "error": str(e),
                },
            }
