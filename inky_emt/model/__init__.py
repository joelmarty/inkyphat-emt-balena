from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Arrival:
    line: str
    stop: str
    destination: str
    arrives_in: int
    distance: int

    def fmt_est(self) -> str:
        if self.arrives_in == 999999:
            return '45mn+'
        if self.arrives_in < 60:
            return '1mn!'
        return f'{divmod(self.arrives_in, 60)[0]}mn'


@dataclass(frozen=True)
class ArrivalInfo:
    stop_name: str
    arrivals: List[Arrival]
    incident: bool
