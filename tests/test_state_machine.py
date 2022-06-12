from unittest.mock import patch 
import pytest
from state import State, Entity
import dataclasses
from state.signals import ns, disconnect_signals_from  
from state.repository import flush_state_database



@dataclasses.dataclass
class Toaster(Entity):
    toast_color:int 
    heater_on:bool = False 
    timer_armed:bool = False
    arm_timer_for_toast_color: int|None = None 

    def arm_timer_event(self, sender, **kwargs): 
        self.timer_armed = True 
        self.arm_timer_for_toast_color = self.toast_color

    def switch_heater_on(self, sender, **kwargs): 
        self.heater_on = True 

    class StateConfig: 
        heating = State(initial=True, on_entry='switch_heater_on', 
                        on={'DO_BAKE': 'baking', 
                            'DO_TOAST': 'toasting', 
                            'DOOR_OPEN': 'door_open'})   
        toasting = State(initial=True, on_entry='arm_timer_event', 
                        substate_of = 'heating', )
        baking = State(substate_of='heating') 
        door_open = State(on={'DOOR_CLOSE': 'heating'}) 

@pytest.fixture
def toaster(): 
    toaster_ = Toaster('toaster', toast_color=3) 
    toaster_.start()
    yield toaster_
    flush_state_database() 
    disconnect_signals_from(ns)
    toaster_.stop() 

#@pytest.mark.skip
@patch.object(Toaster, '_interpret')
def test_interpreter_is_called(mock_interpreter): 
    toaster = Toaster('toaster', toast_color=3) 
    mock_interpreter.assert_called()

def test_repository_database_is_not_empty_after_state_machine_init(toaster): 
    assert bool(toaster._repo._database) 

#@pytest.mark.skip
def test_repository_database_is_empty_after_flushing(toaster):
    flush_state_database()
    assert bool(toaster._repo._database) is False
    

def test_child_method_on_tree(toaster): 
    from state.tree import Vertex
    tree = toaster._repo._database['toaster'] 
    children = tree.children('heating') 
    assert set(children) == {Vertex('baking'), Vertex('toasting')}

    children = tree.children('ROOT') 
    assert set(children) == {Vertex('heating'), Vertex('door_open')}
    
def test_parent_method_on_tree(toaster): 
    from state.tree import Vertex
    tree = toaster._repo._database['toaster'] 
    parent = tree.parent('heating') 
    assert parent == Vertex('ROOT')
    
def test_get_lca_method_on_tree(toaster): 
    from state.tree import Vertex
    tree = toaster._repo._database['toaster'] 
    lca = tree.get_lca('baking', 'door_open') 
    assert lca == Vertex('ROOT')

def test_get_lca_method_on_tree_swap_source_dest(toaster): 
    from state.tree import Vertex
    tree = toaster._repo._database['toaster'] 
    lca = tree.get_lca(dest='baking', source='door_open') 
    assert lca == Vertex('ROOT')

def test_get_lca_method_on_tree_substate(toaster): 
    from state.tree import Vertex
    tree = toaster._repo._database['toaster'] 
    lca = tree.get_lca('baking', 'toasting') 
    assert lca == Vertex('heating')

def test_get_lca_method_on_tree_ancestor(toaster): 
    from state.tree import Vertex
    tree = toaster._repo._database['toaster'] 
    lca = tree.get_lca('baking', 'ROOT') 
    assert lca == Vertex('ROOT')
    
def test_entry_handler_is_called_when_entry_signal_is_emitted(toaster): 
    from state.signals import ENTRY
    heating_state = toaster._repo.get(toaster.name, name='heating')
    ENTRY.send(heating_state)
    
    assert toaster.heater_on


def test_event_signals_do_connect(toaster): 
    from state.signals import ns 
    assert bool(ns.signal('DO_BAKE').receivers)
    assert bool(ns.signal('DO_TOAST').receivers)
    assert bool(ns.signal('DOOR_OPEN').receivers)
    assert bool(ns.signal('DOOR_CLOSE').receivers)

def test_state_machine_starts_in_initial_state(toaster):
    assert toaster.isin('toasting')

    
def test_state_transitions_to_target_state_on_event_emitted( toaster): 
    toaster.dispatch('DOOR_OPEN')
    assert toaster.isin('door_open')


def test_state_transitions_to_target_state_and_enters_initial_substate(toaster): 
    toaster.dispatch('DOOR_OPEN')
    toaster.dispatch('DOOR_CLOSE')
    assert toaster.isin('toasting')


def test_state_transitions_on_do_bake_event(toaster): 
    toaster.dispatch('DO_BAKE')
    assert toaster.isin('baking')


def test_state_transitions_on_do_toast_event(toaster): 
    toaster.dispatch('DOOR_OPEN')
    toaster.dispatch('DOOR_CLOSE')
    toaster.dispatch('DO_BAKE') 
    toaster.dispatch('DO_TOAST')
    assert toaster.isin('toasting')


def test_entry_action_fires_on_entry_into_state(toaster): 
    assert toaster.heater_on
    assert toaster.timer_armed
    assert toaster.arm_timer_for_toast_color == 3
