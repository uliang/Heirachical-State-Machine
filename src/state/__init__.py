from __future__ import annotations
import dataclasses

from blinker.base import Signal

from state.events import Event 


UNSET = 'UNSET'
UNHANDLED = 'UNHANDLED'
UNSET_EVENT = Event(UNSET)


@dataclasses.dataclass(eq=True)
class State: 
    name: str = '' 
    _children: list[State] = dataclasses.field(
            default_factory=list, 
            compare=False, 
            repr=True)

    parent: State = dataclasses.field(
            compare=False, 
            repr=False, 
            init=False)

    def add_substate(self, substate:State)->State: 
        self._children.append(substate)
        substate.parent = self
        return substate

    def should_initially_enter(self) -> bool: 
        return False
   
    @property
    def is_leaf(self) -> bool: 
        return not bool(self._children)

    def __iter__(self): 
        return iter(self._children)


UNSET_STATE = State(UNSET)
UNHANDLED_STATE = State(UNHANDLED)


@dataclasses.dataclass
class InitialState: 
    component: State = dataclasses.field(default=None, 
            init=True, repr=False) 

    def add_substate(self, substate:State): 
        self.component.add_substate(substate)
    
    def should_initially_enter(self) -> bool: 
        return True  

    @property 
    def is_leaf(self) -> bool: 
        return self.component.is_leaf 

    def __iter__(self): 
        return iter(self.component)

    def __eq__(self, state:State) -> bool: 
        return self.component == state

    def __repr__(self) -> str: 
        return repr(self.component)

    @property
    def _children(self)-> list[State]: 
        return self.component._children

    @property
    def parent(self) -> State: 
        return self.component.parent

    @parent.setter
    def parent(self, state: State): 
        self.component.parent = state

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
class StateMachine: 
    parent = None 
    _children: list[State] = dataclasses.field(
            default_factory=list, 
            init=False)
    current_state: State = dataclasses.field(
        default=UNSET_STATE, 
        init=False) 
    _transition_registry: dict[str, Transition] = dataclasses.field(default_factory=dict) 

    def start(self): 
        head = self 
        level = self._children 
        while not head.is_leaf: 
            for child_state in level:
                if child_state.should_initially_enter():
                    head = child_state
                    level = head._children
                    break
        self.current_state = head  
    
    def dispatch(self, sender, event:Event): 
        dest_state = self._transition_registry[event.name].do_transition(self)
        if dest_state is not UNHANDLED_STATE: 
            self.current_state = dest_state

    def subscribe(self, event_emitter:Signal): 
        event_emitter.connect(self.dispatch)

    def get_current_state(self) -> State: 
        return self.current_state

    @property
    def is_leaf(self) -> bool: 
        return not bool(self._children)


@dataclasses.dataclass
class StateMachineBuilder: 
    name : str 
    machine: StateMachine = dataclasses.field(
            default_factory=StateMachine)

    def add_state(self, state:State): 
        self.machine._children.append(state)

    def get_machine(self) -> StateMachine: 
        return self.machine 

    def add_triggered_transition(self, trigger:Event, transition: Transition): 
        self.machine._transition_registry[trigger.name] = transition 
