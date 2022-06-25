from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, ClassVar

from state.signals import ENTRY, EXIT
from state.signals import EXECUTE_ALONG_INITIAL_PATH
from state.signals import ns
from state.model import State
from state.repository import StateRepository
from state.transitions import Transition
from state.protocols import Repository
from state.tree import Vertex
import blinker


def NOOP(sender):
    pass


@dataclass
class VertexPointer:
    _head: Vertex
    _exit_path: list[Vertex] = field(init=False, default_factory=list)
    _entry_path: list[Vertex] = field(init=False, default_factory=list)

    def handle(self, signal: blinker.Signal, payload):
        self._entry_path, self._exit_path = [], []
        start = temp = self._head
        while True:
            if temp.name == "ROOT":
                return

            try:
                _, dest = next(iter(signal.send(temp)))
            except StopIteration:
                _, temp = next(iter(REQUEST_VERTEX.send(self, key=temp.parent)))
                continue

            _, lca = next(iter(REQUEST_LCA.send(self, source=temp, dest=dest)))
            EXECUTE_ALONG_PATH.send(
                self, source=start, dest=lca, callback=self._collect_exit_path
            )
            EXECUTE_ALONG_PATH.send(
                self, source=dest, dest=lca, callback=self._collect_entry_path
            )
            for vertex in self._exit_path[:-1]:
                EXIT.send(vertex)

            for vertex in reversed(self._entry_path[:-1]):
                ENTRY.send(vertex)

            self._entry_path = []
            _, final = next(
                iter(
                    EXECUTE_ALONG_INITIAL_PATH.send(
                        dest, callback=self._collect_entry_path
                    )
                )
            )

            for vertex in self._entry_path[1:]:
                ENTRY.send(vertex)

            self._head = final
            return

    def _collect_exit_path(self, vertex: Vertex):
        self._exit_path.append(vertex)

    def _collect_entry_path(self, vertex: Vertex):
        self._entry_path.append(vertex)

    def points_to(self, name: str) -> bool:
        return self._head.name == name


@dataclass
class Entity:
    name: str

    _current_state: VertexPointer = field(init=False, repr=False, default=None)
    _parent2initialstate: dict[str, Vertex] = field(default_factory=dict, init=False)
    _repo: Repository[Vertex] = field(init=False, default=None)
    _transitions: list[Transition] = field(init=False, default_factory=list)

    _config_classname: ClassVar[str] = "StateConfig"

    def _interpret(self):
        config = getattr(self, self._config_classname)
        for name in dir(config):
            match getattr(config, name):
                case State(
                    on_entry=handle_entry,
                    on_exit=handle_exit,
                    initial=initial,
                    parent=parent,
                    on=transition_object,
                ):

                    this_state = self._repo.get_or_create(name)
                    parent_state = self._repo.get_or_create(parent)
                    this_state.parent = parent_state
                    parent_state.children.append(this_state)

                    EXECUTE_ALONG_INITIAL_PATH.connect(
                        self.visit_path_to_initial_state, this_state
                    )

                    for handler_name, signal in zip(
                        (handle_entry, handle_exit), (ENTRY, EXIT)
                    ):
                        handler = getattr(self, handler_name, NOOP)
                        signal.connect(handler, this_state)

                    if initial:
                        self._parent2initialstate[parent] = this_state

                    for trigger, dest_name in transition_object.items():
                        dest = self._repo.get_or_create(dest_name)
                        transition = Transition(trigger, source=this_state, dest=dest)
                        self._transitions.append(transition)
                case _:

                    pass

    def __post_init__(self):
        self._repo = StateRepository(self.name)

        root = self._repo.get("ROOT")
        self._current_state = VertexPointer(root)

        self._interpret()

    def isin(self, state_id: str) -> bool:
        return self._current_state.points_to(state_id)

    def dispatch(self, trigger: str, payload=None):
        signal = ns.signal(trigger)
        self._current_state.handle(signal, payload)

    def start(self):
        root_state = self._repo.get("ROOT")
        final = self.visit_path_to_initial_state(root_state, callback=ENTRY.send)
        self._current_state._head = final

    def stop(self):
        ...

    def visit_path_to_initial_state(
        self, sender: Vertex, callback: Callable[[Vertex], None]
    ):
        vertex = sender
        while True:
            callback(vertex)
            if vertex.name in self._parent2initialstate:
                vertex = self._parent2initialstate[vertex.name]
                continue
            return vertex
