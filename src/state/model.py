from __future__ import annotations

import dataclasses


ROOT = "ROOT"
UNSET = "UNSET"


@dataclasses.dataclass
class State:
    on_entry: str = UNSET
    initial: bool  = False
    substate_of: str = ROOT
    on: dict[str, str] = dataclasses.field(default_factory=dict)
