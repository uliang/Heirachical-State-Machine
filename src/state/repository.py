from typing import Protocol 
from state.tree import Tree
from state.model import State


class ISignal(Protocol): 
    def connect(self, receiver, sender=None): 
        ... 


class StateRepository(Tree[State]): 
    def __init__(self, add_state_signal:ISignal): 
        super().__init__()
        add_state_signal.connect(self.add_state)

    def add_state(self, state:State, *, name:str): 
        self._vertices[name] = state 
        parent_name = state.substate_of
        parent = self._vertices[parent_name] 
        self._edges.append((parent, state))


