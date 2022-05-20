import blinker

ns = blinker.Namespace() 

postman: blinker.Signal = ns.signal('postman') 
entry_signal: blinker.Signal = ns.signal('entry')
update_repository: blinker.Signal = ns.signal('update_repository')
