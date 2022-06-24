import blinker

ns = blinker.Namespace()

REQUEST_VERTEX = ns.signal(
    "REQUEST_VERTEX", doc="Emitted to recover a vertex from tree"
)
REQUEST_LCA = ns.signal(
    "REQUEST_LCA", doc="Emitted to request lca of two nodes in a tree"
)
EXECUTE_ALONG_PATH = ns.signal(
    "EXECUTE_ALONG_PATH",
    doc="Emitted to request receiver to emit signals for all senders from source vertex to destination vertex",
)
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
