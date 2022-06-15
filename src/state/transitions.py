import dataclasses
from state.tree import Vertex


@dataclasses.dataclass
class Transition:
    source: Vertex
    dest: Vertex

    def __call__(self, sender: Vertex, context, payload):
        ...
