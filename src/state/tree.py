from __future__ import annotations
from functools import partial
from typing import Callable, Literal
import dataclasses
from collections import defaultdict
from operator import attrgetter


@dataclasses.dataclass
class Vertex:
    _name: str = "UNSET"

    children: list[Vertex] = dataclasses.field(default_factory=list)
    depth: int = 0

    _parent: Vertex | Literal["UNSET"] = "UNSET"
    _tree: Tree | Literal["UNSET"] = "UNSET"

    def __eq__(self, other: Vertex | Literal["UNSET"]) -> bool:
        match other:
            case "UNSET" as unset:
                result = self._name == unset
            case Vertex(_name=name):
                result = name == self._name
            case _:
                raise ValueError
        return result

    def __repr__(self) -> str:
        parent_name = self._parent.name if self._parent != "UNSET" else "UNSET"
        return (
            f"<Vertex: name={self._name}, children=[{[c.name for c in self.children]}]"
            f", parent={parent_name}, depth={self.depth}>"
        )

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, other: Tree):
        if self._tree == "UNSET":
            self._tree = other

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name == "UNSET":
            self._name = value

    @property
    def parent(self) -> Vertex:
        return self._parent

    @parent.setter
    def parent(self, value: Vertex):
        if self._parent == "UNSET":
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
        vertex.tree = self

    def __contains__(self, key) -> bool:
        return key in self._vertices

    def get_lca(self, source: Vertex, dest: Vertex) -> Vertex:
        if not self._euler_tour:
            raise NotImplemented(
                "Euler tour not performed. Vertex depth is not defined. Please call finalize method."
            )

        i = self._euler_tour.index(source)
        j = self._euler_tour.index(dest)
        subarray = (
            self._euler_tour[i : j + 1] if i <= j else self._euler_tour[j : i + 1]
        )
        lca_node = min(subarray, key=attrgetter("depth"))
        return lca_node

    def dfs(self, vertex: Vertex):
        stack = [vertex]
        while stack:
            vtx = stack.pop()
            yield vtx
            if not vtx.children:
                yield vtx.parent
                continue
            else:
                for child in reversed(vtx.children):
                    stack.append(child)

    def finalize(self):
        if not self._euler_tour:
            root = self["ROOT"]
            visited = [root]
            for vertex in self.dfs(root):
                if vertex not in visited:
                    visited.append(vertex)
                    vertex.depth = vertex.parent.depth + 1
                self._euler_tour.append(vertex)

    def get_path(
        self,
        source: Vertex,
        dest: Vertex,
    ):
        if not self._euler_tour:
            raise NotImplemented(
                "Euler tour not performed. Vertex depth is not defined. Please call finalize method."
            )

        buffer = []
        should_reverse = source.depth < dest.depth

        if should_reverse:
            source, dest = dest, source

        temp = source
        while True:
            buffer.append(temp)
            if temp == dest:
                return buffer[::-1] if should_reverse else buffer
            temp = temp.parent
            if temp == "UNSET":
                raise ValueError("source and dest do not lie on the same path")
