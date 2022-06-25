import dataclasses
from state.tree import Vertex
from state.signals import ns


@dataclasses.dataclass
class Transition:
    trigger: dataclasses.InitVar[str]
    source: dataclasses.InitVar[Vertex]
    dest: dataclasses.InitVar[Vertex]

    _source2dest: dict[str, Vertex] = dataclasses.field(
        init=False, default_factory=dict
    )

    def __post_init__(self, trigger, source, dest):
        signal = ns.signal(trigger)
        signal.connect(self, source)

        self._source2dest[source.name] = dest

    def __call__(self, sender: Vertex):
        dest = self._source2dest[sender.name]
        return dest


@dataclasses.dataclass
class InitialTransition:
    source: dataclasses.InitVar[Vertex]
    dest: dataclasses.InitVar[Vertex]

    _parent2init: dict[str, Vertex] = dataclasses.field(
        default_factory=dict, init=False
    )

    def __post_init__(self, source, dest):
        signal = ns.signal("INIT")
        signal.connect(self, source)
        self._parent2init[source.name] = dest

    def __call__(self, sender: Vertex):
        dest = self._parent2init[sender.name]
        return dest
