import blinker

ns = blinker.Namespace()

ENTRY = ns.signal("ENTRY", doc="Emitted when state is entered")
EXIT = ns.signal("EXIT", doc="Emitted when state is exitted")
INIT = ns.signal(
    "INIT",
    doc="Emitted when parent state is enter to transition to initial child state",
)


def disconnect_signals_from(namespace: blinker.Namespace):
    for signal in namespace.values():
        for receiver in signal.receivers_for(blinker.ANY):
            signal.disconnect(receiver)
