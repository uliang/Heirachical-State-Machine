from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar

from state.signals import ENTRY, INITIALLY_TRANSITION, HANDLED, EXIT
from state.signals import REQUEST_LCA
from state.signals import ns
from state.model import State
from state.repository import StateRepository
from state.transitions import Transition
from state.protocols import Repository
from state.tree import Vertex, VertexPointer


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
    _current_state: VertexPointer = field(
        init=False, repr=False, default_factory=VertexPointer
    )
    _parent2initialstate: dict[str, Vertex] = field(default_factory=dict, init=False)
    _repo: Repository[Vertex] = field(init=False)

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

                    this_state = self._repo.get(name)
                    this_state.parent = parent
                    for handler_name, signal in zip(
                        (handle_entry, handle_exit), (ENTRY, EXIT)
                    ):
                        handler = getattr(self, handler_name, NOOP)
                        signal.connect(handler, this_state)
                    if initial:
                        self._parent2initialstate[parent] = this_state
                        INITIALLY_TRANSITION.connect(self.enter_initial_state, this_state)

                    for trigger, dest_name in transition_object.items():
                        dest = self._repo.get(dest_name)
                        transition = Transition(trigger, source=this_state, dest=dest)
                        HANDLED.connect(self._current_state.set_head, transition)

                    self._repo.insert(this_state)
                case _:

                    pass

    def __post_init__(self):
        self._repo = StateRepository(self.name)
        self._interpret()

        REQUEST_LCA.connect(self._repo.tree.get_lca, self._current_state)

    def isin(self, state_id: str) -> bool:
        return self._current_state.points_to(state_id)

    def dispatch(self, trigger: str, payload=None):
        signal = ns.signal(trigger)
        self._current_state.handle(signal, payload)

    def start(self):
        root_state = self._repo.get("ROOT")
        self.enter_initial_state(root_state)
        self._current_state.commit()

    def stop(self):
        ...

    def enter_initial_state(self, sender: Vertex):
        vertex = sender
        while True:
            ENTRY.send(vertex)
            if vertex.name not in self._parent2initialstate:
                self._current_state.set_head(vertex)
                return vertex.name

            vertex = self._parent2initialstate[vertex.name]
