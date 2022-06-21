from __future__ import annotations
from functools import partial
from typing import TypeVar, Callable
import dataclasses
from collections import defaultdict
from operator import attrgetter


T = TypeVar("T")


@dataclasses.dataclass
class Vertex:
    name: str = ""
    children: list[str] = dataclasses.field(default_factory=list)
    parent: str = "UNSET"
    depth: int = 0

    def __eq__(self, other) -> bool:
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)


@dataclasses.dataclass
class VertexPointer:
    _head: list[str] = dataclasses.field(default_factory=list)
    _changed: bool = False

    def points_to(self, name: str) -> bool:
        return name in self._head

    def set_head(self, sender, name: str | None = None):
        self._head = []
        match sender:
            case str(name) | Vertex(name=name):
                self._head.append(name)
            case [*names]:
                self._head.extend(names)
            case _:
                if name:
                    self._head.append(name)
        self._changed = True

    def __iter__(self):
        return iter(self._head)

    def clone(self):
        return VertexPointer(_head=self._head)

    def commit(self):
        self._changed = False

    @property
    def changed(self) -> bool:
        return self._changed


@dataclasses.dataclass
class Tree:
    _vertices: dict[str, Vertex] = dataclasses.field(default_factory=partial(defaultdict, Vertex))

    _euler_tour: list[Vertex] = dataclasses.field(default_factory=list, init=False)

    def add_vertex(self, name: str, parent_name: str):
        vertex = self._vertices[name]
        vertex.name = name
        vertex.parent = parent_name
        parent_vertex = self._vertices[parent_name]
        parent_vertex.name = parent_name
        parent_vertex.children.append(name)
        return vertex

    def __getitem__(self, name: str) -> Vertex:
        return self._vertices[name]

    def children(self, name: str) -> list[Vertex]:
        vertex = self[name]
        return [self[child_name] for child_name in vertex.children]

    def parent(self, name: str) -> Vertex:
        vertex = self[name]
        return self[vertex.parent]

    def leaf(self, name: str) -> bool:
        return not bool(self.children(name))

    def get_lca(self, source: str, dest: str) -> Vertex:
        if not self._euler_tour:
            visited = [Vertex("ROOT")]

            def make_euler(node):
                if node not in visited:
                    node.depth = self[node.parent].depth + 1
                    visited.append(node)
                self._euler_tour.append(node)

            self.dfs("ROOT", callback=make_euler)

        source_node = self[source]
        dest_node = self[dest]
        i = self._euler_tour.index(source_node)
        j = self._euler_tour.index(dest_node)
        subarray = (
            self._euler_tour[i : j + 1] if i <= j else self._euler_tour[j : i + 1]
        )
        lca_node = min(subarray, key=attrgetter("depth"))
        return lca_node

    def dfs(self, name: str, callback: Callable[[Vertex], None]):
        callback(self[name])
        for child_id in self[name].children:
            self.dfs(child_id, callback)
        if (parent_name := self[name].parent) != "UNSET":
            return callback(self[parent_name])
