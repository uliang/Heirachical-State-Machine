import dataclasses
import itertools as it
from typing import Callable
from state.tree import Vertex
from state.signals import INIT, ENTRY, EXIT
from state.signals import ns
from state.signals import first, gen_result


@dataclasses.dataclass
class Transition:
    trigger: dataclasses.InitVar[str]
    source: dataclasses.InitVar[Vertex]
    dest: dataclasses.InitVar[Vertex]
    action: dataclasses.InitVar[Callable] = None

    _actions: list[Callable] = dataclasses.field(init=False, default_factory=list)
    _source2dest: dict[str, Vertex] = dataclasses.field(
        init=False, default_factory=dict
    )

    def __post_init__(self, trigger, source, dest, action):
        signal = ns.signal(trigger)
        signal.connect(self, source)
        if action:
            self._actions.append(action)
        self._source2dest[source.name] = dest

    def __call__(self, sender: Vertex, **payload):
        start = sender
        dest = self._source2dest[sender.name]
        tree = dest.tree

        lca = tree.get_lca(start, dest)

        exit_path = tree.get_path(start, lca)
        exit_path = it.takewhile(lambda v: v != lca, exit_path)

        entry_path = tree.get_path(lca, dest)
        entry_path = it.dropwhile(lambda v: v == lca, entry_path)

        [EXIT.send(v) for v in exit_path]
        for action in self._actions:
            action(**payload)
        [ENTRY.send(v) for v in entry_path]

        successors = [gen_result(INIT, dest)]
        while successors:
            if vertex := first(successors.pop()):
                ENTRY.send(vertex)
                successors.append(gen_result(INIT, vertex))
                dest = vertex

        return dest
