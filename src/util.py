import json
import random
from pathlib import Path


def rand_between(a, b):
    return random.randint(a, b) if a < b else a


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def next_idx(jsonl_path: Path) -> int:
    if not jsonl_path.exists():
        return 1
    with jsonl_path.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f) + 1
