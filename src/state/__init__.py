from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar

from state.signals import ENTRY, INITIALLY_TRANSITION, HANDLED
from state.signals import ns
from state.model import State
from state.repository import StateRepository
from state.transitions import Transition
from state.protocols import Repository
from state.tree import VertexPointer


def NOOP(sender):
    pass


@dataclass
class Entity:
    name: str
    _current_state:VertexPointer = field(init=False, repr=False, default_factory=VertexPointer) 
    _ishandled: bool = field(default=False, init=False, repr=False)

    def toggle_handled(self, sender, value):
        self._ishandled = value

    _repo: ClassVar[Repository[State]] = StateRepository()
    _config_classname: ClassVar[str] = "StateConfig"

    def _interpret(self):
        config = getattr(self, self._config_classname)
        for name in dir(config):
            match getattr(config, name):
                case State(
                    on_entry=handle_entry,
                    initial=initial,
                    substate_of=parent,
                    on=transition_object,
                ):

                    this_state = self._repo.insert(
                        self.name, name=name, parent_name=parent
                    )

                    handler = getattr(self, handle_entry, NOOP)
                    ENTRY.connect(handler, this_state)

                    for signal_name, next_state_name in transition_object.items():
                        signal = ns.signal(signal_name)
                        next_state = self._repo.get(self.name, name=next_state_name)
                        transition = Transition(this_state, next_state)
                        signal.connect(transition, this_state, weak=False)
                        HANDLED.connect(self.toggle_handled, transition)

                    if initial:
                        parent_state = self._repo.get(self.name, name=parent)
                        initial_transition = Transition(parent_state, this_state)
                        INITIALLY_TRANSITION.connect(
                            initial_transition, parent_state, weak=False
                        )
                case _:
                    pass

    def __post_init__(self):
        self._interpret()

        root_state = self._repo.get(self.name, name="ROOT")
        INITIALLY_TRANSITION.send(root_state, context=self)

    def isin(self, state_id: str) -> bool:
        return self._current_state.points_to(state_id) 

    def dispatch(self, trigger: str):
        ...

    def start(self):
        ...

    def stop(self):
        ...

    def set(self, key: str):
        self._current_state.set_head(key)

    class StateConfig:
        pass
