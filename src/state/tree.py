from typing import Generic, TypeVar, Callable
import dataclasses



T = TypeVar('T')


@dataclasses.dataclass
class Tree(Generic[T]): 
    _vertices: dict[str, T] = dataclasses.field(
        default_factory=dict) 
    _edges:list[tuple[str, str]] = dataclasses.field(
        default_factory=list) 
   

    def get_child_ids(self, node_id:str) -> list[str]: 
        child_id_list = [child for parent, child in self._edges 
            if parent == node_id] 
        return child_id_list

    def get_parent_id(self, node_id:str) -> str: 
        parent_id = next(parent for parent,child in self._edges
            if child == node_id) 
        return parent_id

    def children(self, node_id:str) -> list[T]: 
        child_ids = self.get_child_ids(node_id)
        return [self._vertices[child_id] for child_id 
                in child_ids]

    def parent(self, node_id:str) -> T: 
        parent_id = self.get_parent_id(node_id)
        return self._vertices[parent_id]

    def leaf(self, node_id:str) -> bool: 
        return not bool(self.children(node_id))

    def get_lca(self, source:str, dest:str)-> T: 
        ... 

    def walk(self, node_id:str, callback:Callable[[T], None]): 
        node = self._vertices[node_id]
        callback(node) 
        for child_id in self.get_child_ids(node): 
            self.walk(child_id, callback)

