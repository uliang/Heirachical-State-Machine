from typing import (Protocol, TypeVar, ClassVar, 
                    Callable) 


class Connectable(Protocol): 
    def connect(self, receiver, sender=None): 
        ... 


class ConfigMetaSpec(Protocol): 
    config_classname:ClassVar[str]
    interpreter:ClassVar[Callable]

