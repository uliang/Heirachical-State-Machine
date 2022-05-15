from __future__ import annotations
import dataclasses
from typing import Optional

from blinker.base import Signal

from state.events import Event 


UNSET = 'UNSET'
UNHANDLED = 'UNHANDLED'
UNSET_EVENT = Event(UNSET)


@dataclasses.dataclass(eq=True)
class State: 
    name: str = '' 
    depth: int = dataclasses.field(default=0, 
        compare=False, 
        init=False, 
        repr=True)

    def should_initially_enter(self) -> bool: 
        return False



UNSET = State('UNSET')
UNHANDLED_STATE = State(UNHANDLED)

@dataclasses.dataclass
class InitialState: 
    component: State = dataclasses.field(default=None, 
            init=True, repr=False) 
    
    def should_initially_enter(self) -> bool: 
        return True  

    @property 
    def depth(self) -> int: 
        return self.component.depth 

    @depth.setter
    def depth(self, value:int): 
        self.component.depth = value

    def __repr__(self) -> str: 
        return repr(self.component)

    def __eq__(self, other:State) -> bool: 
        return self.component == other 


@dataclasses.dataclass
class Transition: 
    source: State 
    dest: State 

    def do_transition(self, machine:StateMachine) -> State: 
        head = machine.get_current_state() 
        while self.source != head: 
            head = head.parent
            if head is None:
                return UNHANDLED_STATE 
        return self.dest


@dataclasses.dataclass
class Tree: 
    _vertices: list[State] = dataclasses.field(
        default_factory=list) 
    _edges:list[tuple[State, State]] = dataclasses.field(
        default_factory=list) 
    _ROOT: State = dataclasses.field(
        default=State('ROOT'))

    def children(self, this_node:State) -> list[State]: 
        return [child for parent, child in self._edges 
            if parent == this_node 
            and child.depth > this_node.depth]

    def parent(self, this_node: State) -> State: 
        return next(parent for parent,child in self._edges
            if child == this_node 
            and parent.depth < this_node.depth)

    def leaf(self, this_node: State) -> bool: 
        return not bool(self.children(this_node))



@dataclasses.dataclass
class StateMachine: 
    _state_tree: Tree = dataclasses.field(
        default_factory=Tree, 
        init=False)

    _current_state: State = dataclasses.field(
        default=UNSET, 
        init=False) 
    _transition_registry: dict[str, Transition] = \
        dataclasses.field(default_factory=dict, 
        init=False) 

    def start(self): 
        ROOT = self._state_tree._ROOT
        self.set_current_state(ROOT)

    def dispatch(self, sender, event:Event): 
        dest_state = self._transition_registry[event.name].do_transition(self)
        if dest_state is not UNHANDLED_STATE: 
            self._current_state = dest_state

    def subscribe(self, event_emitter:Signal): 
        event_emitter.connect(self.dispatch)

    def get_current_state(self) -> State: 
            return self._current_state

    def set_current_state(self, state): 
        children = self._state_tree.children
        leaf = self._state_tree.leaf
        head = state

        while not leaf(head): 
            for child in children(head):
                if child.should_initially_enter():
                    head = child
                    break
        self._current_state = head  


@dataclasses.dataclass
class StateMachineBuilder: 
    name : str 
    machine: StateMachine = dataclasses.field(
            default_factory=StateMachine)

    def add_state(self, state:State, *, substate_of: Optional[State] = None) -> State: 
        parent = substate_of if substate_of else self.machine._state_tree._ROOT
        state.depth = parent.depth + 1
        self.machine._state_tree._vertices.append(state) 
        self.machine._state_tree._edges.append((parent, state))
        return state

    def get_machine(self) -> StateMachine: 
        return self.machine 

    def add_triggered_transition(self, trigger:Event, transition: Transition): 
        self.machine._transition_registry[trigger.name] = transition 
