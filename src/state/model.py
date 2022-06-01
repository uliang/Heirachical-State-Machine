from __future__ import annotations 

import dataclasses 


ROOT = 'ROOT'
UNSET = 'UNSET'


@dataclasses.dataclass
class State: 
    on_entry: str = UNSET
    initial: bool|None = None 
    substate_of: str = ROOT 
    on: dict[str, str] = dataclasses.field(default_factory=dict)

    depth: int = dataclasses.field(default=0, 
        compare=False, 
        init=False, 
        repr=True)
    
    def should_initially_enter(self) -> bool: 
        return False

    def __eq__(self, other:State)-> bool: 
        return self.name == other.name
