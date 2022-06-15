import dataclasses
from state.tree import Vertex
from state.protocols import Settable
from state.signals import INITIALLY_TRANSITION


@dataclasses.dataclass
class Transition:
    source: Vertex
    dest: Vertex

    def __call__(self, sender: Vertex, context: Settable, payload=None):
        context.set(self.dest.name)
        INITIALLY_TRANSITION.send(self.dest, context=context, payload=payload)
