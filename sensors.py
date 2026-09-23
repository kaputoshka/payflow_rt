import random
# sensors.py
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Reading:
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)

class GatewayLatencySensor:


    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._base = 60.0

    def read(self) -> Reading:
        self._base += self._rng.uniform(-4, 5)
        self._base = max(20.0, min(self._base, 400.0))
        return Reading(value=round(self._base, 1), unit="мс")


class AvailabilitySensor:


    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._base = 99.5

    def read(self) -> Reading:
        self._base += self._rng.uniform(-1.5, 1.0)
        self._base = max(40.0, min(self._base, 100.0))
        return Reading(value=round(self._base, 1), unit="%")


class TrafficSensor:

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._base = 8.0

    def read(self) -> Reading:
        self._base += self._rng.uniform(-1, 1.5)
        self._base = max(1.0, min(self._base, 60.0))
        return Reading(value=round(self._base, 1), unit="оп/с")