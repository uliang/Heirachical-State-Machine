from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Literal
from types import MethodType

from state.signals import ENTRY, EXIT 
from state.signals import ns
from state.signals import gen_result, first
from state.model import State
from state.repository import StateRepository
from state.transitions import Transition
from state.protocols import Repository
from state.tree import Vertex


@dataclass
class Entity:
    name: str

    _current_state: Vertex | Literal["UNSET"] = field(default="UNSET", init=False)
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
                        if handler_name != "UNSET":
                            handler = getattr(self, handler_name)
                            action = self._bind_to_sender(handler_name, handler)

                            signal.connect(action, this_state)

                    if initial:
                        transition = Transition("INIT", parent_state, this_state)
                        self._transitions.append(transition)

                    for trigger, dest_name in transition_object.items():
                        match dest_name: 
                            case str(dest_name): 
                                dest = self._repo.get_or_create(dest_name)
                                transition = Transition(trigger, source=this_state, dest=dest)
                            case {"action": action_handler_name }:
                                handler = getattr(self, action_handler_name) 
                                transition = Transition(trigger, source=this_state, dest=this_state, action=handler) 
                        self._transitions.append(transition)


                case _:
                    pass

    def __post_init__(self):
        self._repo = StateRepository(self.name)

        root = self._repo.get("ROOT")

        self._current_state = root

        self._interpret()
        self._repo.tree.finalize()

    def _bind_to_sender(self, action_name: str, action: Callable):
        def action_wrapper(self, sender, **kwargs):
            return action(**kwargs)

        method = MethodType(action_wrapper, self)
        setattr(self, action_name, method)
        return method

    def isin(self, state_id: str) -> bool:
        if state_id == 'ROOT': 
            return True
        head = self._current_state
        while head != self._repo.get('ROOT'): 
            if result := head.name == state_id:
                return result 
            head = head.parent
        return False


    def dispatch(self, trigger: str, **payload):
        signal = ns.signal(trigger)
        root = self._repo.get("ROOT")
        start, dest = self._current_state, None
        tree = root.tree

        for vertex in tree.get_path(start, root):
            if result := first(gen_result(signal, vertex, **payload)):
                dest = result

        if dest:
            self._current_state = dest

    def start(self):
        self.dispatch("INIT")

    def stop(self):
        ...
