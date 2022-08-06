from dataclasses import dataclass


@dataclass
class BinaryForceControl:
    DISABLE: str = "Disable"
    FORCE_OPEN: str = "Force OPEN"
    FORCE_CLOSE: str = "Force CLOSE"
    CHOICE_TUPLE: tuple = (DISABLE, FORCE_OPEN, FORCE_CLOSE,)


class ForceStatus(object):
    def __init__(self, actuator: str):
        self.actuator: str = actuator

    @property
    def force_idle(self) -> str:
        return f'{self.actuator} not forced'

    @property
    def force_open(self) -> str:
        return f'{self.actuator} is forced to OPEN'

    @property
    def force_close(self) -> str:
        return f'{self.actuator} is forced to CLOSE'
