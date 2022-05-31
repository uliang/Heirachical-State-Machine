from __future__ import annotations
import dataclasses
import functools
from typing import Callable, Type

import blinker

from state.tree import Tree
from state.signals import ADD_NODE


# from state.signals import update_repository

UNHANDLED = 'UNHANDLED'


class StateNotFound(Exception): 
    def __init__(self, message, *args): 
        super().__init__(message, *args)


class EventEmitterUnset(Exception): 
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)


class MachineNotStarted(Exception): 
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)


ROOT = 'ROOT'
UNSET = 'UNSET'


@dataclasses.dataclass
class State: 
    on_entry: str = UNSET
    initial: bool|None = None 
    substate_of: str = ROOT 
    on: dict[str, str] = dataclasses.field(default_factory=dict)

    depth: int = dataclasses.field(default=0, 
        compare=False, 
        init=False, 
        repr=True)
    
    def should_initially_enter(self) -> bool: 
        return False

    def __eq__(self, other:State)-> bool: 
        return self.name == other.name


# UNSET = State('UNSET')


# @dataclasses.dataclass 
# class StateRepository: 
#     _database: dict[str, State] = dataclasses.field(default_factory=dict)  
   
#     def __post_init__(self): 
#         update_repository.connect(self.update) 

#     def insert(self, state:State):
#         self._database[state.name] = state

#     def get(self, id: str) -> State: 
#         return self._database[id]

#     def update(self, sender, state:State): 
#         try: 
#             self._database[state.name] = state 
#         except KeyError: 
#             ...
#             # TODO: raise StateNotFound


@dataclasses.dataclass
class Transition: 
    source: State 
    dest: State 
    # _trigger: Event = dataclasses.field(init=False) 

    def do_transition(self, machine) -> State: 
        tree = machine._state_tree
        lca = tree.get_lca(self.source, self.dest)
        machine.set_current_state(self.dest)

    def add_trigger(self, trigger): 
        self._trigger = trigger



#@dataclasses.dataclass
#class StateMachine: 
#    # _ROOT: State = dataclasses.field(
#    #     default=State('ROOT'), 
#    #     init=False)

#    _state_tree: Tree = dataclasses.field(
#        default_factory=Tree, 
#        init=False)
#    _current_state: State = dataclasses.field(
#        default=UNSET, 
#        init=False) 
#    _transition_registry: dict[str, Transition] = \
#        dataclasses.field(default_factory=dict, 
#        init=False) 
#    _context: dict = dataclasses.field(default_factory=dict) 

#    def __post_init__(self): 
#        ...
#        # self._event_emitter:blinker.Signal = postman
#        # postman.connect(self.dispatch)

#    def start(self): 
#        ROOT = self._ROOT
#        self._state_tree._vertices.append(ROOT)
#        self.set_current_state(ROOT)

#    def stop(self): 
#        self._event_emitter.disconnect(self.dispatch) 

#    def dispatch(self, sender, event:Event): 
#        current_state = self.get_current_state()
#        # 
#        if current_state is UNSET: 
#            raise MachineNotStarted("State machine has not been started. "  
#            "Call the start method on StateMachine before post any events to the machine.")
#        transition: str | Transition = self._transition_registry.get(
#            (event.name, current_state.name), UNHANDLED)
#        # if transition is UNHANDLED:   
#        #     raise 
#        transition.do_transition(self)
        
#    def get_current_state(self) -> State: 
#        return self._current_state

#    def set_current_state(self, state: State): 
#        pass 
#        # children = self._state_tree.children
#        # leaf = self._state_tree.leaf
#        # head = state

#        # while not leaf(head): 
#        #     for child in children(head):
#        #         if child.should_initially_enter():
#        #             entry_signal.send(child, **self._context)
#        #             head = child
#        #             break
#        # self._current_state = head  
    
#    def set_context(self, context:dict[str, Any]):
#        self._context = context

#    def isin(self, state_key:str) -> bool: 
#        ... 

# @dataclasses.dataclass
# class StateMachineBuilder: 
#     name : str 
#     machine: StateMachine = dataclasses.field(
#             default_factory=StateMachine)

#     def connect_event_emitter(self, event_emitter:blinker.Signal): 
#         self.machine._event_emitter = event_emitter
#         event_emitter.connect(self.machine.dispatch)

#     def add_state(self, state:State, *, substate_of: Optional[State] = None) -> State: 
#         parent = substate_of if substate_of else self.machine._ROOT
#         state.depth = parent.depth + 1
#         self.machine._state_tree._vertices.append(state) 
#         self.machine._state_tree._edges.append((parent, state))
#         update_repository.send(state=state)

#     def get_machine(self) -> StateMachine: 
#         if self.machine._event_emitter is None: 
#             raise EventEmitterUnset("Event emiiter has not been injected. Call set_event_emitter method with event emitter before obtaining machine.")
#         return self.machine 

#     def add_transition(self, transition: Transition): 
#         registry = self.machine._transition_registry
#         def register_transition(state:State): 
#             trigger_name = transition._trigger.name
#             registry[trigger_name, state.name] = transition 
        
#         walk = self.machine._state_tree.walk
#         walk(transition.source, register_transition)


class StateConfig: 
    ...


def setup_state_machine(config:Type[StateConfig]):
    for name in dir(config):
        classvar = getattr(config, name)
        match classvar: 
            case State(on_entry=handle_entry, initial=initial, substate_of=parent, 
                       on=transition_object): 
                ADD_NODE.send(classvar, name=name)
            case _: 
                pass

    
class EntityMeta(type): 
    def __new__(cls, name, bases, namespace, repoclass=None,  **kwargs): 
        namespace = dict(namespace)
        klass = super().__new__(cls, name, bases, namespace)
        if repoclass: 
            add_node_signal = kwargs.pop('add_node_signal')
            repoclass(add_node_signal)
        if 'StateConfig' in namespace:
            stateconfig = namespace.pop('StateConfig') 
            setup_state_machine(stateconfig)
        return klass 


class StateRepository(Tree[State]): 
    def __init__(self, add_node_signal:blinker.Signal): 
        super().__init__()
        add_node_signal.connect(self.add_node)

    def add_node(self, node:State, *, name:str): 
        self._vertices[name] = node 
        parent_name = node.substate_of
        parent = self._vertices[parent_name] 
        self._edges.append((parent, node))


class Entity(metaclass=EntityMeta, repoclass=StateRepository, 
             add_node_signal=ADD_NODE): 
    def isin(self, state_key:str)-> bool: 
        ...

    def dispatch(self, trigger:str): 
        ... 

    def start(self): 
        ... 

    def stop(self): 
        ... 


