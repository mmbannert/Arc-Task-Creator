from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Stimulus:
    id: str
    rule: str  # e.g. "color_inversion"
    family: str  # e.g. "recolor"
    params: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)
