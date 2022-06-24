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
        return other.name == self._name

    def __hash__(self):
        return hash(self._name)

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
class Tree:
    _vertices: dict[str, Vertex] = dataclasses.field(
        default_factory=partial(defaultdict, Vertex)
    )

    _euler_tour: list[Vertex] = dataclasses.field(default_factory=list, init=False)

    def __getitem__(self, name: str) -> Vertex:
        return self._vertices[name]

    def __setitem__(self, key: str, vertex: Vertex):
        self._vertices[key] = vertex

    def get_vertex(self, sender, key) -> Vertex:
        return self._vertices[key]

    def get_lca(self, sender, source: Vertex, dest: Vertex) -> Vertex:
        if not self._euler_tour:
            root = self["ROOT"]
            visited = [root]

            def make_euler(node):
                if node not in visited:
                    node.depth = self[node.parent].depth + 1
                    visited.append(node)
                self._euler_tour.append(node)

            self.dfs(root, callback=make_euler)

        i = self._euler_tour.index(source)
        j = self._euler_tour.index(dest)
        subarray = (
            self._euler_tour[i : j + 1] if i <= j else self._euler_tour[j : i + 1]
        )
        lca_node = min(subarray, key=attrgetter("depth"))
        return lca_node

    def dfs(self, vertex: Vertex, callback: Callable[[Vertex], None]):
        callback(vertex)
        for child_id in vertex.children:
            self.dfs(self[child_id], callback)
        if (parent_name := vertex.parent) != "UNSET":
            return callback(self[parent_name])

    def execute_along_path(
        self, sender, source: Vertex, dest: Vertex, callback: Callable[[Vertex], None]
    ):
        temp = source
        while True:
            callback(temp)
            temp = self[temp.parent]
            if temp.name == dest.parent:
                return
