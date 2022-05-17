from unittest.mock import create_autospec
import pytest
from state import MachineNotStarted
from state import StateRepository
from state import StateMachineBuilder
from state import State, InitialState
from state import Transition
from state.signals import postman, entry_signal
from state.events import Event

@pytest.fixture 
def heater_on(): 
    def heater_on_spec():
        ...
    return create_autospec(heater_on_spec)

@pytest.fixture 
def arm_time_event(): 
    def arm_time_event_spec(toast_color): 
        ... 
    return create_autospec(spec=arm_time_event_spec) 

@pytest.fixture 
def state_repository(): 
    repo = StateRepository() 
    repo.add(State('heating')) 
    repo.add(State('toasting')) 
    repo.add(State('baking')) 
    repo.add(State('door_open')) 
    return repo 

@pytest.fixture
def factory(state_repository): 
    toaster_factory = StateMachineBuilder('toaster')
   
    heating = state_repository.get('heating') 
    toaster_factory.add_state(InitialState(heating))

    toasting = state_repository.get('toasting') 
    toaster_factory.add_state(InitialState(toasting), substate_of=heating)

    baking = state_repository.get('baking') 
    toaster_factory.add_state(baking, substate_of=heating) 

    door_open = state_repository.get('door_open')
    toaster_factory.add_state(door_open) 

    door_open_trans = Transition(heating, door_open) 
    door_open_trans.add_trigger(Event('DOOR_OPEN')) 
    toaster_factory.add_transition(door_open_trans)
    
    door_close_trans = Transition(door_open, heating) 
    door_close_trans.add_trigger(Event('DOOR_CLOSE')) 
    toaster_factory.add_transition(door_close_trans) 

    do_bake_trans = Transition(heating, baking) 
    do_bake_trans.add_trigger(Event('DO_BAKE'))
    toaster_factory.add_transition(do_bake_trans) 

    do_toast_trans = Transition(heating, toasting) 
    do_toast_trans.add_trigger(Event('DO_TOAST'))
    toaster_factory.add_transition(do_toast_trans) 

    return toaster_factory 


@pytest.fixture
def connect_entry_signals(state_repository, arm_time_event, heater_on): 
    heating = state_repository.get('heating') 
    entry_signal.connect(heater_on, heating)

    toasting = state_repository.get('toasting') 
    entry_signal.connect(arm_time_event, toasting) 

    yield
    entry_signal.disconnect(heater_on)
    entry_signal.disconnect(arm_time_event)


@pytest.fixture 
def setup_unstarted_machine(factory): 
    machine = factory.get_machine() 
    yield 
    postman.disconnect(machine.dispatch)
    

@pytest.fixture
def machine(factory): 
    machine = factory.get_machine()
    machine.set_context({"toast_color": 3})
    machine.start()
    yield machine 
    machine.stop()


@pytest.mark.usefixtures('connect_entry_signals')
def test_state_machine_builder_do_build(factory): 
    machine = factory.get_machine()
    assert machine is not None 


@pytest.mark.usefixtures('connect_entry_signals')
def test_state_machine_starts_in_initial_state(machine):
    assert machine.get_current_state() == State('toasting')

    
@pytest.mark.usefixtures('setup_unstarted_machine')
def test_machine_cannot_transition_if_not_started(): 
    with pytest.raises(MachineNotStarted) as excinfo: 
        postman.send(event=Event('DOOR_OPEN'))
    assert str(excinfo.value) == "State machine has not been started. Call the start method on StateMachine before post any events to the machine."
        

@pytest.mark.usefixtures('connect_entry_signals')
def test_state_transitions_to_target_state_on_event_emitted(machine): 
    postman.send(event=Event('DOOR_OPEN'))
    assert machine.get_current_state() == State('door_open')


@pytest.mark.usefixtures('connect_entry_signals')
def test_state_transitions_to_target_state_and_enters_initial_substate(machine): 
    postman.send(event=Event('DOOR_OPEN')) 
    postman.send(event=Event('DOOR_CLOSE')) 
    assert machine.get_current_state() == State('toasting')


@pytest.mark.usefixtures('connect_entry_signals')
def test_state_transitions_on_do_bake_event(machine): 
    postman.send(event=Event('DO_BAKE')) 
    assert machine.get_current_state() == State('baking') 


@pytest.mark.usefixtures('connect_entry_signals')
def test_state_transitions_on_do_toast_event(machine): 
    postman.send(event=Event('DOOR_OPEN'))
    postman.send(event=Event('DOOR_CLOSE'))
    postman.send(event=Event('DO_BAKE')) 
    postman.send(event=Event('DO_TOAST'))
    assert machine.get_current_state() == State('toasting') 


@pytest.mark.usefixtures('connect_entry_signals', 'machine' ) 
def test_entry_action_fires_on_entry_into_state(arm_time_event, heater_on): 
    heater_on.assert_called()
    arm_time_event.assert_called_with(3)
