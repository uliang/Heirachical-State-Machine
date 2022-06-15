from typing import Protocol, ClassVar, Callable, TypeVar


T = TypeVar("T")


class Connectable(Protocol):
    def connect(self, receiver, sender=None):
        ...


class Settable(Protocol):
    def set(self, key: str):
        ...


class ConfigMetaSpec(Protocol):
    config_classname: ClassVar[str]
    interpreter: ClassVar[Callable]


class Repository(Protocol[T]):
    def insert(self, entity_name: str, /, name: str, state: T):
        ...

    def get(self, entity_name: str, /, name: str) -> T:
        ...

    def flush(self):
        ...
