from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from state.tree import Tree, Vertex


@dataclass
class StateRepository:

    _database: dict[str, Tree] = field(
        default_factory=partial(defaultdict, Tree), init=False
    )

    def insert(self, entity_name: str, /, name: str, parent_name: str) -> Vertex:
        tree = self._database[entity_name]
        return tree.add_vertex(name=name, parent_name=parent_name)

    def get(self, entity_name: str, /, name: str) -> Vertex:
        return self._database[entity_name][name]

    def flush(self):
        self._database = defaultdict(Tree)
