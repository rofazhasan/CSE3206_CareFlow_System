import uuid
from datetime import datetime


class Appointment:
    def __init__(self, patient_id: str, doctor_id: str, scheduled_time: str, reason: str, fee: float = 1000.0, status: str = "PENDING", appointment_id: str = None):
        self.appointment_id = appointment_id or str(uuid.uuid4())[:8]
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.scheduled_time = scheduled_time
        self.reason = reason
        self.fee = float(fee)
        self.status = status.upper()  # PENDING, CONFIRMED, COMPLETED, CANCELLED
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    def confirm(self):
        if self.status == "CANCELLED":
            raise ValueError("Cannot confirm a cancelled appointment.")
        self.status = "CONFIRMED"

    def complete(self):
        if self.status != "CONFIRMED":
            raise ValueError("Only confirmed appointments can be completed.")
        self.status = "COMPLETED"

    def cancel(self):
        if self.status == "COMPLETED":
            raise ValueError("Cannot cancel an already completed appointment.")
        self.status = "CANCELLED"

    def to_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "scheduled_time": self.scheduled_time,
            "reason": self.reason,
            "fee": self.fee,
            "status": self.status,
            "created_at": self.created_at,
        }
