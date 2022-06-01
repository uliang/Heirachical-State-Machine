import dataclasses 
from state.model import State


@dataclasses.dataclass
class Transition: 
    source: State 
    dest: State 

    def do_transition(self, machine) -> State: 
        tree = machine._state_tree
        lca = tree.get_lca(self.source, self.dest)
        machine.set_current_state(self.dest)

    def add_trigger(self, trigger): 
        self._trigger = trigger

