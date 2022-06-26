from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar

from state.signals import ENTRY, EXIT, INIT
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

    def handle(self, signal: blinker.Signal, payload=None):
        tree = self._head.tree
        dest, root, start = None, tree["ROOT"], self._head

        def signal_did_handle(vertex:Vertex): 
            result = signal.send(vertex)
            [[_, dest]] = result if result else [(None, False)]
            return dest

        if (dest := tree.search_until(start=start, end=root, callback=signal_did_handle)) is None: 
            return

        lca = tree.get_lca(source=start, dest=dest)

        for vertex in tree.get_path(start, lca)[:-1]:
            EXIT.send(vertex)

        for vertex in tree.get_path(lca, dest)[1:]:
            ENTRY.send(vertex)

        vertex, buffer = dest, [dest]
        while vertex := INIT.send(vertex):
            [[_, vertex]] = vertex
            buffer.append(vertex)

        for vertex in buffer[1:]:
            ENTRY.send(vertex)

        self._head = buffer[-1]

    def points_to(self, name: str) -> bool:
        return self._head.name == name


@dataclass
class Entity:
    name: str

    _current_state: VertexPointer = field(init=False, repr=False, default=None)
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

                    for handler_name, signal in zip(
                        (handle_entry, handle_exit), (ENTRY, EXIT)
                    ):
                        handler = getattr(self, handler_name, NOOP)
                        signal.connect(handler, this_state)

                    if initial:
                        transition = Transition("INIT", parent_state, this_state)
                        self._transitions.append(transition)

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
        self._repo.tree.finalize()

    def isin(self, state_id: str) -> bool:
        return self._current_state.points_to(state_id)

    def dispatch(self, trigger: str, payload=None):
        signal = ns.signal(trigger)
        self._current_state.handle(signal, payload)

    def start(self):
        self.dispatch("INIT")

    def stop(self):
        ...
