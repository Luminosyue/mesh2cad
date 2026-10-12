"""Read-only geometry compatibility graph; Qwen never mutates it."""
from pathlib import Path
import yaml
PATH=Path(__file__).resolve().parents[1]/"config/builder_compatibility.yaml"
def load_graph(): return yaml.safe_load(PATH.read_text(encoding="utf-8"))
