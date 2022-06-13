
import blinker

ns = blinker.Namespace() 

ENTRY = ns.signal('Emitted when state is entered') 
INITIALLY_TRANSITION = ns.signal('Emitted when parent state is entered to indicate that'
                                 ' transition to initial substate should occur.')

def disconnect_signals_from(namespace: blinker.Namespace): 
    for signal in namespace.values(): 
        for receiver in signal.receivers_for(blinker.ANY): 
            signal.disconnect(receiver)

