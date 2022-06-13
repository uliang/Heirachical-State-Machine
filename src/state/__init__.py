from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar 

from state.signals import ENTRY, INITIALLY_TRANSITION
from state.model import State
from state.repository import StateRepository
from state.signals import ns
from state.transitions import Transition
from state.protocols import Repository


def NOOP(sender): pass 


@dataclass
class Entity:  
    name: str 
    _current_state:State|None = field(default=None, init=False)

    _repo:ClassVar[Repository[State]] = StateRepository()
    _config_classname:ClassVar[str] = 'StateConfig' 

    def _interpret(self): 
        config = getattr(self, self._config_classname)
        saved_transition_configs = []
        for name in dir(config):
            classvar = getattr(config, name)
            match classvar: 
                case State(on_entry=handle_entry, initial=initial,  
                           substate_of=parent, on=transition_object): 

                    this_state = classvar
                    self._repo.insert(self.name, name=name, state=this_state)

                    handler = getattr(self, handle_entry, NOOP) 
                    ENTRY.connect(handler, this_state)

                    transition_configs = [(name, signal_name, next_state_name) for 
                            signal_name, next_state_name in transition_object.items()]
                    saved_transition_configs.extend(transition_configs)

                    if initial:
                        parent_state = self._repo.get(self.name, name=parent)
                        initial_transition = Transition(parent_state, dest=this_state)
                        INITIALLY_TRANSITION.connect(initial_transition,parent_state, weak=False) 
                case _: 
                    pass

        for this_state_name, signal_name, next_state_name in saved_transition_configs: 
            signal = ns.signal(signal_name)
            source_ = self._repo.get(self.name, name=this_state_name)
            dest = self._repo.get(self.name, name=next_state_name)
            transition = Transition(source_, dest)
            signal.connect(transition, source_, weak=False)

    def __post_init__(self): 
        self._interpret() 

    def isin(self, state_id:str)-> bool: 
        return self._current_state == \
            self._repo.get(self.name, name=state_id)

    def dispatch(self, trigger:str): 
        ... 

    def start(self): 
        ... 

    def stop(self): 
        ...

    class StateConfig:  pass  


