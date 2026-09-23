from models import PaymentStatus

ALLOWED_TRANSITIONS: dict[PaymentStatus, list[PaymentStatus]] = {
    PaymentStatus.CREATED: [PaymentStatus.VALIDATING],
    PaymentStatus.VALIDATING: [PaymentStatus.RISK_CHECK,PaymentStatus.ERROR],
    PaymentStatus.RISK_CHECK: [PaymentStatus.ROUTING,PaymentStatus.DECLINED],
    PaymentStatus.ROUTING: [PaymentStatus.PROCESSING, PaymentStatus.ERROR],
    PaymentStatus.PROCESSING: [PaymentStatus.APPROVED, PaymentStatus.DECLINED],
    PaymentStatus.APPROVED: [],
    PaymentStatus.DECLINED: [],
    PaymentStatus.ERROR: [],
}

def can_transition(current: PaymentStatus, target: PaymentStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]