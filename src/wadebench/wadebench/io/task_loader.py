import json
from pathlib import Path
from typing import List, Dict, Any, Generator

class TaskLoader:
    def __init__(self, split_file_path: str):
        self.split_file_path = Path(split_file_path)

    def iter_tasks(self) -> Generator[Dict[str, Any], None, None]:
        if not self.split_file_path.exists():
            raise FileNotFoundError(f"Split file not found: {self.split_file_path}")
            
        with open(self.split_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
                    
    def load_all_tasks(self) -> List[Dict[str, Any]]:
        return list(self.iter_tasks())
