import pytest
from state import MachineNotStarted, EventEmitterUnset 
from state import StateMachineBuilder
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
    
    door_close_trans = Transition(door_open, heating) 
    toaster_factory.add_triggered_transition(Event('DOOR_CLOSE'), door_close_trans) 

    do_bake_trans = Transition(heating, baking) 
    toaster_factory.add_triggered_transition(Event('DO_BAKE'), do_bake_trans) 

    do_toast_trans = Transition(heating, toasting) 
    toaster_factory.add_triggered_transition(Event('DO_TOAST'), do_toast_trans) 

    return toaster_factory 


@pytest.fixture
def inject_event_emitter(factory): 
    factory.connect_event_emitter(postman)


@pytest.fixture 
def inject_event_emiiter_and_disconnect(factory): 
    factory.connect_event_emitter(postman) 
    yield 
    machine = factory.get_machine() 
    postman.disconnect(machine.dispatch)
    

@pytest.fixture
def machine(factory): 
    machine = factory.get_machine()
    machine.start()
    yield machine 
    machine.stop()


@pytest.mark.usefixtures('inject_event_emiiter_and_disconnect')
def test_state_machine_builder_do_build(factory): 
    machine = factory.get_machine()
    assert machine is not None 


@pytest.mark.usefixtures('inject_event_emitter')
def test_state_machine_starts_in_initial_state(machine):
    assert machine.get_current_state() == State('toasting')


def test_factory_raises_event_emitter_not_set_if_get_machine_method_is_called_before_injecting_event_emitter(factory): 
    with pytest.raises(EventEmitterUnset) as excinfo: 
        machine = factory.get_machine() 
    assert str(excinfo.value) == "Event emiiter has not been injected. Call set_event_emitter method with event emitter before obtaining machine."

    
@pytest.mark.usefixtures('inject_event_emiiter_and_disconnect')
def test_machine_cannot_transition_if_not_started(factory): 
    with pytest.raises(MachineNotStarted) as excinfo: 
        postman.send(event=Event('DOOR_OPEN'))
    assert str(excinfo.value) == "State machine has not been started. Call the start method on StateMachine before post any events to the machine."
        

@pytest.mark.usefixtures('inject_event_emitter')
def test_state_transitions_to_target_state_on_event_emitted(machine): 
    postman.send(event=Event('DOOR_OPEN'))
    assert machine.get_current_state() == State('door_open')


@pytest.mark.usefixtures('inject_event_emitter') 
def test_state_transitions_to_target_state_and_enters_initial_substate(machine): 
    postman.send(event=Event('DOOR_OPEN')) 
    postman.send(event=Event('DOOR_CLOSE')) 
    assert machine.get_current_state() == State('toasting')


@pytest.mark.usefixtures('inject_event_emitter') 
def test_state_transitions_on_do_bake_event(machine): 
    postman.send(event=Event('DO_BAKE')) 
    assert machine.get_current_state() == State('baking') 


@pytest.mark.usefixtures('inject_event_emitter')
def test_state_transitions_on_do_toast_event(machine): 
    postman.send(event=Event('DOOR_OPEN'))
    postman.send(event=Event('DOOR_CLOSE'))
    postman.send(event=Event('DO_BAKE')) 
    postman.send(event=Event('DO_TOAST'))
    assert machine.get_current_state() == State('toasting') 


# @pytest.mark.usefixtures('inject_event_emitter') 
# def test_entry_action_fires_on_entry_into_state(machine): 
