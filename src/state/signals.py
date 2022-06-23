import blinker

ns = blinker.Namespace()

REQUEST_LCA = ns.signal("Emitter to request lca of two nodes in a tree")
ENTRY = ns.signal("ENTRY", doc="Emitted when state is entered")
EXIT = ns.signal("EXIT", doc="Emitter when state is exitted")
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
