from collections import defaultdict
from dataclasses import dataclass, field, InitVar
from typing import ClassVar 
from state.tree import Tree, Vertex


@dataclass
class StateRepository:
    tree_name: InitVar[str]

    _tree: Tree = field(init=False, default=None)
    _database: ClassVar[defaultdict] =  defaultdict(Tree)

    def __post_init__(self, tree_name): 
        self._tree = self._database[tree_name]
        self._tree['ROOT'] = Vertex('ROOT')
        
    @property 
    def tree(self) -> Tree: 
        return self._tree

    def insert(self, vertex:Vertex,/) -> Vertex:
        self._tree[vertex.name] = vertex
        parent = self._tree[vertex.parent]
        parent.children.append(vertex.name)
        
        return vertex

    def get(self, name:str) -> Vertex:
        vertex =  self._tree[name]
        vertex.name = name
        return vertex

    def flush(self):
        self._database = defaultdict(Tree)
        
        
