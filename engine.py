import random
import uuid

from models import Payment, PaymentStatus
from transitions import ALLOWED_TRANSITIONS
from sensors import GatewayLatencySensor, AvailabilitySensor, TrafficSensor


class SimulationEngine:
    def __init__(self) -> None:
        self.payments: list[Payment] = []
        self.is_running: bool = False
        self._counter: int = 0

        self.gateway_latency_sensor = GatewayLatencySensor()
        self.availability_sensor = AvailabilitySensor()
        self.traffic_sensor = TrafficSensor()

        self.last_latency_reading = None
        self.last_availability_reading = None
        self.last_traffic_reading = None

    def start(self) -> None:
        self.is_running = True

    def pause(self) -> None:
        self.is_running = False

    def stop(self) -> None:
        self.is_running = False
        self.payments.clear()
        self._counter = 0

    def tick(self) -> list[Payment]:
        if not self.is_running:
            return []

        self.last_latency_reading = self.gateway_latency_sensor.read()
        self.last_availability_reading = self.availability_sensor.read()
        self.last_traffic_reading = self.traffic_sensor.read()

        changed: list[Payment] = []

        spawn_chance = min(self.last_traffic_reading.value / 20, 0.9)
        if random.random() < spawn_chance:
            changed.append(self._spawn_payment())

        for payment in self.payments:
            if self._advance(payment):
                changed.append(payment)

        return changed

    def _spawn_payment(self) -> Payment:
        self._counter += 1
        payment = Payment(
            payment_id=f"TX-{self._counter:03d}-{uuid.uuid4().hex[:4].upper()}",
            amount_rubles=random.randint(150, 25000),
            channel=random.choice(["Основной", "Резервный"]),
        )
        self.payments.append(payment)
        return payment

    def _advance(self, payment: Payment) -> bool:
        possible = ALLOWED_TRANSITIONS[payment.status]
        if not possible:
            return False

        if (
                payment.status == PaymentStatus.ROUTING
                and self.last_availability_reading.value < 90
                and PaymentStatus.ERROR in possible
        ):
            payment.status = PaymentStatus.ERROR
        else:
            payment.status = random.choice(possible)

        payment.latency_ms += int(self.last_latency_reading.value / 3)
        return True