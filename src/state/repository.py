from collections import defaultdict
from dataclasses import dataclass, field
from state.signals import ADD_STATE, GET_STATE, FLUSH_DATABASE
from state.tree import Tree
from state.model import State


@dataclass
class StateRepository: 

    _database: dict[str, Tree[State]] = field(default=None, init=False)
   
    def __post_init__(self): 
        self._database = defaultdict(Tree) 

    @classmethod 
    def with_connections(cls): 
        repo = cls()
        ADD_STATE.connect(repo.add_state)
        GET_STATE.connect(repo.get_state)        
        FLUSH_DATABASE.connect(repo.flush)
        return repo

    def add_state(self, sender:State, /,  entity_name:str, name:str): 
        tree = self._database[entity_name] 
        tree._vertices[name] = sender 
        parent_name = sender.substate_of
        # parent = tree._vertices[parent_name] 
        tree._edges.append((parent_name, name))

    def get_state(self, sender, /, entity_name:str, name:str): 
        return self._database[entity_name]._vertices[name]

    def flush(self, sender, /):
        self._database = {}

def flush_state_database(): 
    FLUSH_DATABASE.send()
