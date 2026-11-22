import json
from pathlib import Path
from typing import Dict, Any


def safe_model_slug(model: str) -> str:
    return str(model).replace('/', '_').replace(':', '_').replace(' ', '_').replace('.', '_')


class OutputWriter:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_prediction(self, prediction: Dict[str, Any]) -> str:
        task_id = prediction.get("task_id", "unknown_task")
        file_path = self.output_dir / f"{task_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(prediction, f, indent=2, ensure_ascii=False)
        return str(file_path)
