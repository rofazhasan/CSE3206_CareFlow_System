import uuid
from datetime import datetime


class Invoice:
    def __init__(self, appointment_id: str, patient_id: str, base_amount: float, discount_amount: float = 0.0, tax_amount: float = 0.0, status: str = "UNPAID", payment_reference: str = "", invoice_id: str = None):
        self.invoice_id = invoice_id or str(uuid.uuid4())[:8]
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.base_amount = float(base_amount)
        self.discount_amount = float(discount_amount)
        self.tax_amount = float(tax_amount)
        self.status = status.upper()  # UNPAID, PAID
        self.payment_reference = payment_reference
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    @property
    def total_payable(self) -> float:
        total = self.base_amount - self.discount_amount + self.tax_amount
        return max(0.0, round(total, 2))

    def mark_as_paid(self, reference: str):
        self.status = "PAID"
        self.payment_reference = reference

    def to_dict(self) -> dict:
        return {
            "invoice_id": self.invoice_id,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "base_amount": self.base_amount,
            "discount_amount": self.discount_amount,
            "tax_amount": self.tax_amount,
            "total_payable": self.total_payable,
            "status": self.status,
            "payment_reference": self.payment_reference,
            "created_at": self.created_at,
        }
