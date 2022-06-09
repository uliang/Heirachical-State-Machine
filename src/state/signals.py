
import blinker

ns = blinker.Namespace() 

ADD_STATE = ns.signal('Emitted when state is to be added to the repository tree')   
GET_STATE = ns.signal('Emiited when state is queried with state_id')
FLUSH_DATABASE = ns.signal('Emitted when state database needs to be emptied')
ENTRY = ns.signal('Emitted when state is entered') 

def disconnect_signals_from(namespace: blinker.Namespace): 
    for signal in namespace.values(): 
        for receiver in signal.receivers_for(blinker.ANY): 
            signal.disconnect(receiver)

