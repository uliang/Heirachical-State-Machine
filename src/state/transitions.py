import dataclasses 
from state.model import State


@dataclasses.dataclass
class Transition: 
    source: State 
    dest: State 

    def __call__(self, sender:State, **kwargs) -> State: 
        ...
