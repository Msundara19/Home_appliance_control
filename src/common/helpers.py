import yaml
from pathlib import Path

def load_config():
    cfg_path = Path(__file__).parent / "config.yaml"
    if not cfg_path.exists():
        # Fall back to example with safe defaults
        cfg_path = Path(__file__).parent / "config.example.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)