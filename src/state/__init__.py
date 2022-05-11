from __future__ import annotations
import dataclasses


UNSET = 'UNSET'


@dataclasses.dataclass(eq=True)
class State: 
    name: str = '' 
    _children: list[State] = dataclasses.field(
            default_factory=list, 
            compare=False, 
            repr=True)

    def add_substate(self, substate:State): 
        self._children.append(substate)

    def should_initially_enter(self) -> bool: 
        return False
   
    @property
    def is_leaf(self) -> bool: 
        return not bool(self._children)

    def __iter__(self): 
        return iter(self._children)


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


@dataclasses.dataclass
class StateMachine: 
    
    _children: list[State] = dataclasses.field(
            default_factory=list, 
            init=False)
    current_state: State = dataclasses.field(
        default=State(UNSET), 
        init=False) 

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

