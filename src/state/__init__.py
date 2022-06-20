from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar

from state.signals import ENTRY, INITIALLY_TRANSITION, HANDLED, EXIT
from state.signals import ns
from state.model import State
from state.repository import StateRepository
from state.transitions import Transition
from state.protocols import Repository
from state.tree import Vertex, VertexPointer


def NOOP(sender):
    pass


@dataclass
class Entity:
    name: str
    _current_state: VertexPointer = field(
        init=False, repr=False, default_factory=VertexPointer
    )
    _parent2initialstate: dict[str, Vertex] = field(default_factory=dict, init=False)

    _repo: ClassVar[Repository[State]] = StateRepository()
    _config_classname: ClassVar[str] = "StateConfig"

    def _interpret(self):
        config = getattr(self, self._config_classname)
        for name in dir(config):
            match getattr(config, name):
                case State(
                    on_entry=handle_entry,
                    on_exit=handle_exit, 
                    initial=initial,
                    substate_of=parent,
                    on=transition_object,
                ):

                    this_state = self._repo.insert(
                        self.name, name=name, parent_name=parent
                    )

                    handler = getattr(self, handle_entry, NOOP)
                    ENTRY.connect(handler, this_state)

                    handler = getattr(self, handle_exit, NOOP)
                    EXIT.connect(handler, this_state)


                    for trigger, next_state_name in transition_object.items():
                        dest = self._repo.get(self.name, next_state_name)
                        transition = Transition(trigger, source=this_state, dest=dest)
                        HANDLED.connect(self._current_state.set_head, transition)

                    if initial:
                        parent_state = self._repo.get(self.name, name=parent)
                        self._parent2initialstate[parent_state.name] = this_state
                        INITIALLY_TRANSITION.connect(
                            self.enter_initial_state, parent_state
                        )
                case _:
                    pass

    def __post_init__(self):
        self._interpret()

        root_state = self._repo.get(self.name, name="ROOT")
        INITIALLY_TRANSITION.send(root_state)
        self._current_state.commit()

    def isin(self, state_id: str) -> bool:
        return self._current_state.points_to(state_id)

    def dispatch(self, trigger: str, payload=None):
        signal = ns.signal(trigger)
        vp = self._current_state.clone()
        exit_path = [] 
        entry_path = [] 
        while not vp.points_to("ROOT"):
            for state_id in vp:
                state = self._repo.get(self.name, name=state_id)
                exit_path.append(state)
                result = signal.send(state)
                if self._current_state.changed:
                    _, dest_state_id = next(iter(result))
                    lca = self._repo[self.name].get_lca(state_id, dest_state_id)
                    # breakpoint()
                    path_head = state 
                    exit_path.append(path_head) 
                    while path_head.name != lca.name: 
                        path_head = self._repo.get(self.name, name=path_head.parent)
                        exit_path.append(path_head) 
                        # if path_head.name != lca.parent:
                        #     break

                    dest_state = self._repo.get(self.name, dest_state_id)
                    path_head = dest_state 
                    entry_path.append(path_head)
                    while path_head.name != lca.name: 
                        path_head = self._repo.get(self.name, name=path_head.parent) 
                        entry_path.append(path_head) 

                    for state in exit_path: 
                        EXIT.send(state) 

                    for state in reversed(entry_path[:-1]): 
                        ENTRY.send(state) 

                    INITIALLY_TRANSITION.send(dest_state)
                    self._current_state.commit()
                    return
                parent = self._repo.get(self.name, name=state.parent)
                vp.set_head(parent.name)

    def start(self):
        ...

    def stop(self):
        ...

    def enter_initial_state(self, sender: Vertex):
        vertex = sender
        while True:
            ENTRY.send(vertex)
            if vertex.name not in self._parent2initialstate:
                self._current_state.set_head(vertex.name)
                return vertex.name
            vertex = self._parent2initialstate[vertex.name]

    class StateConfig:
        pass
