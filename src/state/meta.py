from typing import Callable, Type
from state.protocols import Subscriber, Connectable
from state.signals import INTERPRET_STATE_MACHINE_CONFIG 


class EntityMeta(type): 
    def __new__(cls, name, bases, namespace, 
                repoclass:Subscriber[Connectable]|None=None,
                interpreter:Callable[[Type], None]|None=None, 
                **kwargs:Connectable): 

        namespace = dict(namespace)
        if interpreter: 
            INTERPRET_STATE_MACHINE_CONFIG.connect(interpreter)
        
        if repoclass: 
            repoclass(**kwargs)

        if 'StateConfig' in namespace:
            stateconfig = namespace.pop('StateConfig') 
            INTERPRET_STATE_MACHINE_CONFIG.send(cls, config=stateconfig)

        klass = super().__new__(cls, name, bases, namespace)
        return klass 
