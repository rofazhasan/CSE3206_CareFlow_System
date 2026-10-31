from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


@dataclass
class Invoice:
    appointment_id: str
    patient_id: str
    base_amount: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    status: PaymentStatus = PaymentStatus.UNPAID
    payment_reference: str = ""
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def total_payable(self) -> float:
        return max(0.0, round(self.base_amount - self.discount_amount + self.tax_amount, 2))

    def mark_as_paid(self, reference_id: str) -> None:
        self.status = PaymentStatus.PAID
        self.payment_reference = reference_id

    def to_dict(self) -> dict:
        return {
            "invoice_id": self.invoice_id,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "base_amount": self.base_amount,
            "discount_amount": self.discount_amount,
            "tax_amount": self.tax_amount,
            "total_payable": self.total_payable,
            "status": self.status.value if isinstance(self.status, PaymentStatus) else str(self.status),
            "payment_reference": self.payment_reference,
            "created_at": self.created_at,
        }
