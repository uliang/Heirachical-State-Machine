def test_state_machine_starts_in_initial_state(toaster):
    assert toaster.isin("toasting")


def test_state_transitions_to_target_state_on_event_emitted(toaster):
    toaster.dispatch("DOOR_OPEN")
    assert toaster.isin("door_open")


def test_state_transitions_to_target_state_and_enters_initial_substate(toaster):
    toaster.dispatch("DOOR_OPEN")
    toaster.dispatch("DOOR_CLOSE")
    assert toaster.isin("toasting")


def test_state_transitions_on_do_bake_event(toaster):
    toaster.dispatch("DO_BAKE")
    assert toaster.isin("baking")


def test_state_transitions_on_do_toast_event(toaster):
    toaster.dispatch("DOOR_OPEN")
    toaster.dispatch("DOOR_CLOSE")
    toaster.dispatch("DO_BAKE")
    toaster.dispatch("DO_TOAST")
    assert toaster.isin("toasting")


def test_entry_action_fires_on_entry_into_state(toaster):
    assert toaster.heater_on
    assert toaster.timer_armed
    assert toaster.arm_timer_for_toast_color == 3


def test_exit_action_fires_on_exit_from_state(toaster):
    toaster.dispatch("DOOR_OPEN")

    assert not toaster.heater_on


def test_isin_method_returns_true_for_superstates(toaster):
    assert toaster.isin("heating")
