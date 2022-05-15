import pytest
from state import MachineNotStarted, StateMachineBuilder
from state import State, InitialState
from state import Transition
from state.signals import postman
from state.events import Event


@pytest.fixture
def factory(): 
    toaster_factory = StateMachineBuilder('toaster')

    heating = State('heating') 
    toasting = State('toasting') 
    baking = State('baking')
    
    door_open = State('door_open') 

    heating = toaster_factory.add_state(InitialState(heating))
    toasting = toaster_factory.add_state(InitialState(toasting), substate_of=heating)
    baking = toaster_factory.add_state(baking, substate_of=heating) 
    door_open = toaster_factory.add_state(door_open) 

    door_open_trans = Transition(heating, door_open) 
    toaster_factory.add_triggered_transition(Event('DOOR_OPEN'), door_open_trans)

    return toaster_factory 


@pytest.fixture
def machine(factory): 
    machine = factory.get_machine()
    machine.subscribe(postman)
    yield machine
    machine.unsubscribe(postman)

@pytest.fixture
def setup_machine(machine): 
    machine.start()


def test_state_machine_builder_do_build(factory): 
    machine = factory.get_machine()
    assert machine is not None 

@pytest.mark.usefixtures('setup_machine')
def test_machine_is_in_an_initial_state(machine): 
    assert machine.get_current_state() == State('toasting')

@pytest.mark.usefixtures('machine')
def test_machine_cannot_transition_if_not_started(): 
    with pytest.raises(MachineNotStarted) as excinfo: 
        postman.send(event=Event('DOOR_OPEN'))
    assert str(excinfo.value) == "State machine has not been started. Call the start method on StateMachine before post any events to the machine."
        
@pytest.mark.usefixtures('setup_machine')
def test_state_transitions_to_target_state_on_event_emitted(machine): 
    postman.send(event=Event('DOOR_OPEN'))
    assert machine.get_current_state() == State('door_open')
