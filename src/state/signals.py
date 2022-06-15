import blinker

ns = blinker.Namespace()

ENTRY = ns.signal("ENTRY", doc="Emitted when state is entered")
INITIALLY_TRANSITION = ns.signal(
    "INITIALLY_TRANSITION",
    doc="Emitted when parent state is entered to indicate that"
    " transition to initial substate should occur.",
)
HANDLED = ns.signal("HANDLED", doc="Emitter when transition was handled")


def disconnect_signals_from(namespace: blinker.Namespace):
    for signal in namespace.values():
        for receiver in signal.receivers_for(blinker.ANY):
            signal.disconnect(receiver)
