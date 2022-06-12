from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar 

from state.signals import ENTRY, ADD_STATE, GET_STATE
from state.model import State
from state.repository import StateRepository
from state.signals import ns
from state.transitions import Transition


def NOOP(sender): pass 


@dataclass
class Entity:  
    name: str 
    _current_state:State|None = field(default=None, init=False)

    _repo:ClassVar[StateRepository] = StateRepository()
    _config_classname:ClassVar[str] = 'StateConfig' 

    def _interpret(self): 
        entityname = self.name
        config = getattr(self, self._config_classname)
        saved_transition_configs = {}
        for name in dir(config):
            classvar = getattr(config, name)
            match classvar: 
                case State(on_entry=handle_entry, initial=initial,  
                           substate_of=parent, on=transition_object): 

                    this_state = classvar
                    self._repo.insert(self.name, name=name, state=this_state)

                    handler = getattr(self, handle_entry, NOOP) 
                    ENTRY.connect(handler, this_state)

                    saved_transition_configs[name] = transition_object
                case _: 
                    pass

        for this_state_name, transition_object in saved_transition_configs.items(): 
            for signal_name, next_state_name in transition_object.items(): 
                signal = ns.signal(signal_name)
                source_ = self._repo.get(self.name, name=this_state_name)
                dest = self._repo.get(self.name, name=next_state_name)
                transition = Transition(source_, dest)
                signal.connect(transition, source_, weak=False)
                # breakpoint()

    def __post_init__(self): 
        self._repo.connect_signals()
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


