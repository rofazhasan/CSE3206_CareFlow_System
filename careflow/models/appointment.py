from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class AppointmentStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Appointment:
    patient_id: str
    doctor_id: str
    scheduled_time: str  # ISO-8601 string, e.g. "2026-11-05T10:00:00"
    reason: str
    fee: float = 1000.0
    status: AppointmentStatus = AppointmentStatus.PENDING
    appointment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def confirm(self) -> None:
        if self.status == AppointmentStatus.CANCELLED:
            raise ValueError("Cannot confirm a cancelled appointment.")
        self.status = AppointmentStatus.CONFIRMED

    def complete(self) -> None:
        if self.status != AppointmentStatus.CONFIRMED:
            raise ValueError("Only confirmed appointments can be marked as completed.")
        self.status = AppointmentStatus.COMPLETED

    def cancel(self) -> None:
        if self.status == AppointmentStatus.COMPLETED:
            raise ValueError("Cannot cancel an already completed appointment.")
        self.status = AppointmentStatus.CANCELLED

    def to_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "scheduled_time": self.scheduled_time,
            "reason": self.reason,
            "fee": self.fee,
            "status": self.status.value if isinstance(self.status, AppointmentStatus) else str(self.status),
            "created_at": self.created_at,
        }
