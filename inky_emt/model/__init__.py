from dataclasses import dataclass
from typing import List


@dataclass()
class Arrival:
    line: str
    stop: str
    destination: str
    arrives_in: int
    distance: int

    def fmt_arrival(self):
        if self.arrives_in == 99999:
            return '45mn+'
        if self.arrives_in < 60:
            return '1mn!'
        return f'{divmod(self.arrives_in, 60)[0]}mn'


@dataclass()
class ArrivalInfo:
    stop_name: str
    arrivals: List[Arrival]
    incident: bool
