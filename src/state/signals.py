
import blinker


ADD_STATE = blinker.Signal('Emitted when state is to be added to the repository tree')   
GET_STATE = blinker.Signal('Emiited when a certain state is requested')
