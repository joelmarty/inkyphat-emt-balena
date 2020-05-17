from typing import TypedDict, List


class Arrival(TypedDict):
    line: str
    stop: str
    destination: str
    arrives_in: int
    distance: int


class ArrivalInfo(TypedDict):
    stop_name: str
    arrivals: List[Arrival]
    incident: bool
