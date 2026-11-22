from pathlib import Path
import time
import json

from wadebench.baselines.base import BaseAgent
from wadebench.utils.mcp_snapshot_evidence import (
    build_b4_mcp_evidence,
    save_b4_evidence_and_trace,
)
from wadebench.utils.json_utils import extract_json_object, normalize_prediction


class PlaywrightMCPAgentBaseline(BaseAgent):
    name = "b4_playwright_mcp_agent"

    def __init__(
        self,
        model_client,
        schema_loader,
        prompt_path="prompts/b4_playwright_mcp_agent.txt",
        split="dev",
        max_evidence_chars=160000,
    ):
        self.model_client = model_client
        self.schema_loader = schema_loader
        self.prompt_template = Path(prompt_path).read_text(encoding="utf-8")
        self.split = split
        self.max_evidence_chars = max_evidence_chars

    def build_prompt(self, task: dict, schema: dict, evidence: dict) -> str:
        task_for_prompt = {
            "task_id": task.get("task_id"),
            "domain": task.get("domain"),
            "task_type": task.get("task_type"),
            "schema_id": task.get("schema_id"),
            "snapshot_path": task.get("snapshot_path"),
        }

        evidence_for_prompt = dict(evidence)
        evidence_for_prompt.pop("tool_trace", None)

        evidence_json = json.dumps(evidence_for_prompt, indent=2, ensure_ascii=False)

        if len(evidence_json) > self.max_evidence_chars:
            evidence_json = evidence_json[:self.max_evidence_chars] + "\n<!-- EVIDENCE TRUNCATED -->"

        return (
            self.prompt_template
            .replace("{{TASK_JSON}}", json.dumps(task_for_prompt, indent=2, ensure_ascii=False))
            .replace("{{SCHEMA_JSON}}", json.dumps(schema, indent=2, ensure_ascii=False))
            .replace("{{EVIDENCE_JSON}}", evidence_json)
        )

    def repair_json_once(self, bad_output: str) -> tuple:
        repair_prompt = (
            "The previous output was invalid JSON.\n\n"
            "Return only a valid JSON object in this format:\n"
            "{\n  \"records\": [{...}]\n}\n\n"
            "Rules:\n- Extract and include all the valid records from the invalid output.\n- No markdown.\n- No explanation.\n"
            "- First character must be {.\n- Last character must be }.\n\n"
            f"Invalid output:\n{bad_output[:12000]}"
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

            evidence = build_b4_mcp_evidence(task)
            evidence_path, trace_path = save_b4_evidence_and_trace(
                evidence=evidence,
                task_id=task_id,
                split=self.split,
            )

            prompt = self.build_prompt(task, schema, evidence)

            response = self.model_client.complete(prompt=prompt)

            repaired = False
            repair_response = None

            try:
                payload = normalize_prediction(extract_json_object(response.text))
                success = True
                error = None

            except Exception as e:
                try:
                    payload, repair_response = self.repair_json_once(response.text)
                    success = True
                    repaired = True
                    error = f"json_repaired_after_error: {str(e)}"
                except Exception as repair_error:
                    payload = {"records": []}
                    success = False
                    error = f"json_parse_failed: {str(e)} | repair_failed: {str(repair_error)}"

            input_tokens = getattr(response, "input_tokens", 0) + (getattr(repair_response, "input_tokens", 0) if repair_response else 0)
            output_tokens = getattr(response, "output_tokens", 0) + (getattr(repair_response, "output_tokens", 0) if repair_response else 0)
            total_tokens = getattr(response, "total_tokens", 0) + (getattr(repair_response, "total_tokens", 0) if repair_response else 0)

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
                    "evidence_path": evidence_path,
                    "tool_trace_path": trace_path,
                    "error": error,
                },
            }

        except Exception as e:
            return {
                "task_id": task_id,
                "baseline": self.name,
                "model": self.model_client.model_name,
                "domain": domain,
                "schema_id": schema_id,
                "records": [],
                "run_metadata": {
                    "success": False,
                    "json_valid": False,
                    "runtime_success": False,
                    "repaired": False,
                    "latency_seconds": round(time.time() - start, 3),
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "evidence_path": None,
                    "tool_trace_path": None,
                    "error": str(e),
                },
            }
