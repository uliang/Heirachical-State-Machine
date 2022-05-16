from __future__ import annotations
import dataclasses
from typing import Callable, Optional

import blinker 

from state.events import Event 


UNHANDLED = 'UNHANDLED'


class EventEmitterUnset(Exception): 
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)


class MachineNotStarted(Exception): 
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)


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


@dataclasses.dataclass
class InitialState: 
    component: State = dataclasses.field(default=None, 
            init=True, repr=False) 
    
    def should_initially_enter(self) -> bool: 
        return True  

    @property 
    def depth(self) -> int: 
        return self.component.depth 
    
    @property
    def name(self) -> str: 
        return self.component.name

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
        tree = machine._state_tree
        lca = tree.get_lca(self.source, self.dest)
        machine.set_current_state(self.dest)


@dataclasses.dataclass
class Tree: 
    _vertices: list[State] = dataclasses.field(
        default_factory=list) 
    _edges:list[tuple[State, State]] = dataclasses.field(
        default_factory=list) 
   
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

    def get_lca(self, source:State, dest:State)-> State: 
        ... 

    def walk(self, node:State, callback:Callable[[State], None]): 
        callback(node) 
        for child in self.children(node): 
            self.walk(child, callback)


@dataclasses.dataclass
class StateMachine: 
    _ROOT: State = dataclasses.field(
        default=State('ROOT'), 
        init=False)

    _state_tree: Tree = dataclasses.field(
        default_factory=Tree, 
        init=False)
    _current_state: State = dataclasses.field(
        default=UNSET, 
        init=False) 
    _transition_registry: dict[str, Transition] = \
        dataclasses.field(default_factory=dict, 
        init=False) 
    _event_emitter: blinker.Signal = dataclasses.field(
        default=None, 
        init=False)

    def start(self): 
        ROOT = self._ROOT
        self._state_tree._vertices.append(ROOT)
        self.set_current_state(ROOT)

    def dispatch(self, sender, event:Event): 
        current_state = self.get_current_state()
        # breakpoint()
        if current_state is UNSET: 
            raise MachineNotStarted("State machine has not been started. "  
            "Call the start method on StateMachine before post any events to the machine.")
        transition: str | Transition = self._transition_registry.get(
            (event.name, current_state.name), UNHANDLED)
        # if transition is UNHANDLED:   
        #     raise 
        transition.do_transition(self)
        
    def subscribe(self, event_emitter:blinker.Signal): 
        event_emitter.connect(self.dispatch)    

    def unsubscribe(self, event_emitter:blinker.Signal): 
        event_emitter.disconnect(self.dispatch)

    def get_current_state(self) -> State: 
        return self._current_state

    def set_current_state(self, state: State): 
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

    def connect_event_emitter(self, event_emitter:blinker.Signal): 
        self.machine._event_emitter = event_emitter
        event_emitter.connect(self.machine.dispatch)

    def add_state(self, state:State, *, substate_of: Optional[State] = None) -> State: 
        parent = substate_of if substate_of else self.machine._ROOT
        state.depth = parent.depth + 1
        self.machine._state_tree._vertices.append(state) 
        self.machine._state_tree._edges.append((parent, state))
        return state

    def get_machine(self) -> StateMachine: 
        if self.machine._event_emitter is None: 
            raise EventEmitterUnset("Event emiiter has not been injected. Call set_event_emitter method with event emitter before obtaining machine.")
        return self.machine 

    def add_triggered_transition(self, trigger:Event, transition: Transition): 
        registry = self.machine._transition_registry
        def register_transition(state:State): 
            registry[trigger.name, state.name] = transition 
        
        walk = self.machine._state_tree.walk
        walk(transition.source, register_transition)
            
