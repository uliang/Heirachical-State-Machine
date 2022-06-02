from typing import Protocol, TypeVar

T = TypeVar('T')


class Subscriber(Protocol[T]): 
    def __init__(self, **kwargs:T ):
        '''
        init method executes subscription logic on kwargs. 
        '''
        

class Connectable(Protocol): 
    def connect(self, receiver, sender=None): 
        ... 

