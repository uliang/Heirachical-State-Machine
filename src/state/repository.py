from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from state.tree import Tree
from state.model import State


@dataclass
class StateRepository:

    _database: dict[str, Tree[State]] = field(
        default_factory=partial(defaultdict, Tree), init=False
    )

    def insert(self, entity_name: str, /, name: str, state: State):
        tree = self._database[entity_name]
        tree.add_vertex(state, name, parent_name=state.substate_of)

    def get(self, entity_name: str, /, name: str):
        return self._database[entity_name][name].data

    def flush(self):
        self._database = defaultdict(Tree)
