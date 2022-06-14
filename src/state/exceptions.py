class StateNotFound(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


class EventEmitterUnset(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)


class MachineNotStarted(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)
