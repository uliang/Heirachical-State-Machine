import pytest
import dataclasses
from state import Entity
from state.model import State
from state.signals import ns, disconnect_signals_from


@dataclasses.dataclass
class Toaster(Entity):
    toast_color: int
    heater_on: bool = False
    timer_armed: bool = False
    arm_timer_for_toast_color: int | None = None

    def arm_timer_event(self):
        self.timer_armed = True
        self.arm_timer_for_toast_color = self.toast_color

    def switch_heater_on(self):
        self.heater_on = True

    def switch_heater_off(self):
        self.heater_on = False

    class StateConfig:
        heating = State(
            initial=True,
            on_entry="switch_heater_on",
            on_exit="switch_heater_off",
            on={"DO_BAKE": "baking", "DO_TOAST": "toasting", "DOOR_OPEN": "door_open"},
        )
        toasting = State(
            initial=True,
            on_entry="arm_timer_event",
            parent="heating",
        )
        baking = State(parent="heating")
        door_open = State(on={"DOOR_CLOSE": "heating"})


@pytest.fixture
def toaster():
    toaster_ = Toaster("toaster", toast_color=3)
    toaster_.start()
    yield toaster_
    disconnect_signals_from(ns)
    toaster_.stop()
    toaster_._repo.flush()


class Keyboard(Entity):
    display: str = None

    def send_lower_case_scan_code(self, key: str):
        self.display = key.lower()

    def send_upper_case_scan_code(self, key: str):
        self.display = key.upper()

    class StateConfig:
        default = State(
            initial=True,
            on={
                "ANY_KEY": {"action": "send_lower_case_scan_code"},
                "CAPS_LOCK": "caps_locked",
            },
        )
        caps_locked = State(
            on={
                "ANY_KEY": {"action": "send_upper_case_scan_code"},
                "CAPS_LOCK": "default",
            }
        )


@pytest.fixture
def keyboard():
    keyboard_ = Keyboard("keyboard")
    keyboard_.start()
    yield keyboard_
    disconnect_signals_from(ns)
    keyboard_.stop()
    keyboard_._repo.flush()
