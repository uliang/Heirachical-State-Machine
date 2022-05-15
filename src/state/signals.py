import blinker

ns = blinker.Namespace() 

postman:blinker.Signal = ns.signal('postman') 
