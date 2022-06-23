from __future__ import annotations
from functools import partial
from typing import Callable
import dataclasses
from collections import defaultdict
from operator import attrgetter
from state.protocols import Settable
from state.signals import REQUEST_LCA

import blinker


@dataclasses.dataclass
class Vertex:
    _name: str = "UNSET"
    children: list[str] = dataclasses.field(default_factory=list)
    _parent: str = "UNSET"
    depth: int = 0

    def __eq__(self, other) -> bool:
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value != self._name and self._name != "UNSET":
            raise ValueError
        self._name = value

    @property
    def parent(self) -> str:
        return self._parent

    @parent.setter
    def parent(self, value: str):
        if value != self._parent and self._parent != "UNSET":
            raise ValueError
        self._parent = value


@dataclasses.dataclass
class VertexPointer:
    _head: list[Vertex] = dataclasses.field(default_factory=list)
    _handled: bool = False
    _lca : Vertex|str = "UNSET"

    def handle(self, signal: blinker.Signal, payload): 
        start = temp = self._head
        exit_path = [] 
        while True: 
            for vertex in temp: 
                if vertex.name == "ROOT":
                    return 
                exit_path.append(vertex)
                result = signal.send(vertex)
                if self._handled: 
                    for _, dest in result: 
                        REQUEST_LCA.send(self, source=vertex, dest=dest)
                    break 

    def set(self, lca): 
        self._lca = lca 

    def points_to(self, name: str) -> bool:
        return any(name==vertex.name for vertex in self._head)

    def set_head(self, sender:Vertex):
        self._head = [sender]
        self._handled = True

    def __iter__(self):
        return iter(self._head)

    def clone(self):
        return VertexPointer(_head=self._head)

    def commit(self):
        self._handled = False

    @property
    def handled(self) -> bool:
        return self._handled


@dataclasses.dataclass
class Tree:
    _vertices: dict[str, Vertex] = dataclasses.field(
        default_factory=partial(defaultdict, Vertex)
    )

    _euler_tour: list[Vertex] = dataclasses.field(default_factory=list, init=False)

    def __getitem__(self, name: str) -> Vertex:
        return self._vertices[name]

    def __setitem__(self, key: str, vertex: Vertex):
        self._vertices[key] = vertex

    def children(self, name: str) -> list[Vertex]:
        vertex = self[name]
        return [self[child_name] for child_name in vertex.children]

    def parent(self, name: str) -> Vertex:
        vertex = self[name]
        return self[vertex.parent]

    def leaf(self, name: str) -> bool:
        return not bool(self.children(name))

    def get_lca(self, sender:Settable[Vertex],  source: Vertex, dest: Vertex) -> Vertex:
        if not self._euler_tour:
            visited = [self["ROOT"]]

            def make_euler(node):
                if node not in visited:
                    node.depth = self[node.parent].depth + 1
                    visited.append(node)
                self._euler_tour.append(node)

            self.dfs("ROOT", callback=make_euler)

        i = self._euler_tour.index(source)
        j = self._euler_tour.index(dest)
        subarray = (
            self._euler_tour[i : j + 1] if i <= j else self._euler_tour[j : i + 1]
        )
        lca_node = min(subarray, key=attrgetter("depth"))
        sender.set(lca_node)
        return lca_node

    def dfs(self, name: str, callback: Callable[[Vertex], None]):
        callback(self[name])
        for child_id in self[name].children:
            self.dfs(child_id, callback)
        if (parent_name := self[name].parent) != "UNSET":
            return callback(self[parent_name])
