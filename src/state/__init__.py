from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar 

from state.signals import ADD_STATE, GET_STATE
from state.model import State
from state.repository import StateRepository


@dataclass
class Entity:  
    name: str 
    _current_state:State|None = field(default=None, init=False)

    _repo:StateRepository =field(default_factory=StateRepository.with_connections,init=False) 
    _config_classname:ClassVar[str] = 'StateConfig' 

    def _interpret(self): 
        entityname = self.name
        config = getattr(self, self._config_classname)
        for name in dir(config):
            classvar = getattr(config, name)
            match classvar: 
                case State(on_entry=handle_entry, initial=initial,  
                           substate_of=parent, on=transition_object): 
                    ADD_STATE.send(classvar, entity_name=entityname, name=name)
                case _: 
                    pass

    def __post_init__(self): 
        self._interpret() 

    def isin(self, state_id:str)-> bool: 
        return self._current_state == GET_STATE.send(self, name=state_id)     

    def dispatch(self, trigger:str): 
        ... 

    def start(self): 
        ... 

    def stop(self): 
        ... 

    class StateConfig:  pass  


