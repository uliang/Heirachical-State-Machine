import pytest
from state import InitialState, StateMachineBuilder
from state import State


@pytest.fixture
def factory(): 
    toaster_factory = StateMachineBuilder('toaster')

    toasting = State('toasting') 
    baking = State('baking')
    
    heating = State('heating') 
    heating.add_substate(InitialState(toasting)) 
    heating.add_substate(baking)

    toaster_factory.add_state(heating)

    return toaster_factory 


@pytest.fixture
def machine(factory): 
    return factory.get_machine()


def test_state_machine_builder_do_build(factory): 
    machine = factory.get_machine()
    assert machine is not None 


def test_machine_is_in_an_initial_state(machine): 
    machine.start()
    assert machine.get_current_state() == State('toasting')
