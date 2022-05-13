import dataclasses


@dataclasses.dataclass(eq=True)
class Event: 
    name:str = dataclasses.field(compare=True)


