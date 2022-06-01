from __future__ import annotations
from typing import Type

from state.signals import ADD_STATE
from state.model import State
from state.repository import StateRepository


class StateConfig: 
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
    def __new__(cls, name, bases, namespace, repoclass=None,  **kwargs): 
        namespace = dict(namespace)
        klass = super().__new__(cls, name, bases, namespace)
        if repoclass: 
            add_state_signal = kwargs.pop('add_state_signal')
            repoclass(add_state_signal)
        if 'StateConfig' in namespace:
            stateconfig = namespace.pop('StateConfig') 
            setup_state_machine(stateconfig)
        return klass 


class Entity(metaclass=EntityMeta, repoclass=StateRepository, 
             add_state_signal=ADD_STATE): 
    def isin(self, state_key:str)-> bool: 
        ...

    def dispatch(self, trigger:str): 
        ... 

    def start(self): 
        ... 

    def stop(self): 
        ... 


