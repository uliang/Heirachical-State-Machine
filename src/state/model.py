from __future__ import annotations

import dataclasses


ROOT = "ROOT"
UNSET = "UNSET"


@dataclasses.dataclass
class State:
    on_entry: str = UNSET
    on_exit: str = UNSET
    initial: bool = False
    parent: str = ROOT
    on: dict[str, str] = dataclasses.field(default_factory=dict)
