import blinker

ns = blinker.Namespace()

ENTRY = ns.signal("ENTRY", doc="Emitted when state is entered")
EXIT = ns.signal("EXIT", doc="Emitter when state is exitted")
EXECUTE_ALONG_INITIAL_PATH = ns.signal(
    "EXECUTE_ALONG_INITIAL_PATH",
    doc="Emitted when parent state is entered to indicate that"
    " transition to initial substate should occur.",
)


def disconnect_signals_from(namespace: blinker.Namespace):
    for signal in namespace.values():
        for receiver in signal.receivers_for(blinker.ANY):
            signal.disconnect(receiver)
