from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type 

from state.signals import ADD_STATE, GET_STATE
from state.model import State
from state.repository import StateRepository
from state.meta import EntityMeta



def setup_state_machine(sender:Type[EntityMeta], config:Type):
    for name in dir(config):
        classvar = getattr(config, name)
        match classvar: 
            case State(on_entry=handle_entry, initial=initial,  
                       substate_of=parent, on=transition_object): 
                ADD_STATE.send(classvar, name=name)
            case _: 
                pass


@dataclass
class Entity(metaclass=EntityMeta, repoclass=StateRepository, 
             interpreter=setup_state_machine, 
             add_state_signal=ADD_STATE, 
             get_state_signal=GET_STATE): 

    _current_state:State = field(default=None, init=False)

    def isin(self, state_id:str)-> bool: 
        return self._current_state == GET_STATE.send(self, name=state_id)     

    def dispatch(self, trigger:str): 
        ... 

    def start(self): 
        ... 

    def stop(self): 
        ... 


