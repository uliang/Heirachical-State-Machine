
import blinker

ns = blinker.Namespace() 

ENTRY = ns.signal('Emitted when state is entered') 

def disconnect_signals_from(namespace: blinker.Namespace): 
    for signal in namespace.values(): 
        for receiver in signal.receivers_for(blinker.ANY): 
            signal.disconnect(receiver)

