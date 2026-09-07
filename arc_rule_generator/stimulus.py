from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Stimulus:
    id: str
    rule: str  # e.g. "cross_plus_recolor"
    family: str  # e.g. "color" (inferred)
    params: Dict[str, Any]

    def to_json_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d
