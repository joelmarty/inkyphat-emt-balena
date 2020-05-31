import time
from dataclasses import dataclass
from threading import Thread

from emt.api import EMTClient
from display.inky import ArrivalDisplay


@dataclass
class Configuration:
    refresh_interval: int
    line: str
    stop_id: str


class EMTApp(Thread):
    def __init__(self, api: EMTClient, display: ArrivalDisplay,
                 configuration: Configuration, group=None, name=None):
        super().__init__(group=group, name=name)

        self._api = api
        self._display = display
        self.configuration = configuration
        self._stopped = False

    def run(self) -> None:
        self._api.login()
        while not self._stopped:
            arrivals = self._api.get_arrival_times(self.configuration.stop_id,
                                                   self.configuration.line)
            self._display.show_arrivals(arrivals)
            time.sleep(self.configuration.refresh_interval * 60)

    def stop(self):
        self._stopped = True
