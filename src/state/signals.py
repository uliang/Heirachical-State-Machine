import blinker

ns = blinker.Namespace() 

postman = ns.signal('postman') 
