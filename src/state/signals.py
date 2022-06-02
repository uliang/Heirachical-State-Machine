
import blinker


ADD_STATE = blinker.Signal('Emitted when state is to be added to the repository tree')   
GET_STATE = blinker.Signal('Emiited when state is queried with state_id')
INTERPRET_STATE_MACHINE_CONFIG = blinker.Signal(
        'Emitted when metaclass needs to initialize the state machine.')
