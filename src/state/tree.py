from typing import Generic, TypeVar, Callable
import dataclasses



T = TypeVar('T')


@dataclasses.dataclass
class Tree(Generic[T]): 
    _vertices: dict[str, T] = dataclasses.field(
        default_factory=dict) 
    _edges:list[tuple[T, T]] = dataclasses.field(
        default_factory=list) 
   

    def children(self, this_node:T) -> list[T]: 
        return [child for parent, child in self._edges 
            if parent == this_node] 

    def parent(self, this_node: T) -> T: 
        return next(parent for parent,child in self._edges
            if child == this_node) 

    def leaf(self, this_node: T) -> bool: 
        return not bool(self.children(this_node))

    def get_lca(self, source:T, dest:T)-> T: 
        ... 

    def walk(self, node:T, callback:Callable[[T], None]): 
        callback(node) 
        for child in self.children(node): 
            self.walk(child, callback)

