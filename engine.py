import random
import uuid
from collections import deque

from models import Payment, PaymentStatus
from transitions import ALLOWED_TRANSITIONS
from sensors import GatewayLatencySensor, AvailabilitySensor, TrafficSensor


class SimulationEngine:
    def __init__(self) -> None:
        self.traffic_history: deque[float] = deque(maxlen=120)
        self.latency_history: deque[float] = deque(maxlen=120)
        self.queue_history: deque[float] = deque(maxlen=120)
        self.active_gateway: str = "Основной"

        self.intensity: float = 1.0  # множитель скорости обработки
        self.blocked_terminals: set[str] = set()
        self.events: list[CommandEvent] = []

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
        self.traffic_history.append(self.last_traffic_reading.value)
        self.latency_history.append(self.last_latency_reading.value)
        unfinished = sum(
            1 for p in self.payments
            if p.status not in (PaymentStatus.APPROVED, PaymentStatus.DECLINED, PaymentStatus.ERROR)
        )
        self.queue_history.append(unfinished)
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

    def switch_gateway(self, target: str) -> CommandEvent:
        success = target in ("Основной", "Резервный") and target != self.active_gateway
        if success:
            self.active_gateway = target
        event = CommandEvent(
            CommandType.SWITCH_GATEWAY,
            f"активен {self.active_gateway}",
            success,
        )
        self.events.append(event)
        return event

    def set_intensity(self, value: float) -> CommandEvent:
        success = 0.2 <= value <= 3.0
        if success:
            self.intensity = value
        event = CommandEvent(
            CommandType.SET_INTENSITY,
            f"x{self.intensity:.1f}",
            success,
        )
        self.events.append(event)
        return event

    def retry_processing(self) -> CommandEvent:
        retried = [p for p in self.payments if p.status == PaymentStatus.ERROR]
        for payment in retried:
            payment.status = PaymentStatus.ROUTING
        event = CommandEvent(
            CommandType.RETRY_PROCESSING,
            f"возвращено в обработку: {len(retried)}",
            bool(retried),
        )
        self.events.append(event)
        return event

    def block_terminal(self, terminal_id: str) -> CommandEvent:
        success = bool(terminal_id) and terminal_id not in self.blocked_terminals
        if success:
            self.blocked_terminals.add(terminal_id)
        event = CommandEvent(
            CommandType.BLOCK_TERMINAL,
            terminal_id or "—",
            success,
        )
        self.events.append(event)
        return event