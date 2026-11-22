from typing import Dict, Any

class BaseAgent:
    name = "base"

    def __init__(self, model_client, output_dir: str):
        self.model_client = model_client
        self.output_dir = output_dir

    def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the task and returns a prediction dictionary following the shared format:
        {
          "task_id": "...",
          "baseline": "...",
          "model": "...",
          "domain": "...",
          "schema_id": "...",
          "records": [],
          "run_metadata": {
            "success": True,
            "json_valid": True,
            "latency_seconds": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "error": None
          }
        }
        """
        raise NotImplementedError("Subclasses must implement run_task")
