from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, TypeVar, Protocol
import blinker


from state.signals import ADD_STATE, GET_STATE
from state.model import State
from state.repository import StateRepository


T = TypeVar('T') 


class StateConfig: 
    ...


class RepositoryP(Protocol[T]): 
    def __init__(self, **kwargs:T ):
        ... 


def setup_state_machine(config:Type[StateConfig]):
    for name in dir(config):
        classvar = getattr(config, name)
        match classvar: 
            case State(on_entry=handle_entry, initial=initial,  
                       substate_of=parent, on=transition_object): 
                ADD_STATE.send(classvar, name=name)
            case _: 
                pass

    
class EntityMeta(type): 
    def __new__(cls, name, bases, namespace, repoclass:RepositoryP[blinker.Signal]|None=None,
                **kwargs:blinker.Signal): 
        namespace = dict(namespace)
        klass = super().__new__(cls, name, bases, namespace)
        if repoclass: 
            repoclass(**kwargs)
        if 'StateConfig' in namespace:
            stateconfig = namespace.pop('StateConfig') 
            setup_state_machine(stateconfig)
        return klass 


@dataclass
class Entity(metaclass=EntityMeta, repoclass=StateRepository, 
             add_state_signal=ADD_STATE, 
             get_state_signal=GET_STATE): 

    _current_state:State = field(init=False)

    def isin(self, state_id:str)-> bool: 
        return self._current_state == GET_STATE.send(self, name=state_id)     

    def dispatch(self, trigger:str): 
        ... 

    def start(self): 
        ... 

    def stop(self): 
        ... 


