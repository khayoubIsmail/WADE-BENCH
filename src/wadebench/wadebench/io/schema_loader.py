import json
from pathlib import Path
from typing import Dict, Any

class SchemaLoader:
    def __init__(self, schemas_dir: str = "data/schemas"):
        self.schemas_dir = Path(schemas_dir)

    def load_schema(self, schema_id: str) -> Dict[str, Any]:
        schema_path = self.schemas_dir / f"{schema_id}.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
