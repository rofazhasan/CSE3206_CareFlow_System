from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid


@dataclass
class PrescriptionItem:
    medicine_name: str
    dosage: str  # e.g., "500mg"
    frequency: str  # e.g., "1-0-1 after meal"
    duration_days: int

    def to_dict(self) -> dict:
        return {
            "medicine_name": self.medicine_name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "duration_days": self.duration_days,
        }


@dataclass
class MedicalRecord:
    appointment_id: str
    patient_id: str
    doctor_id: str
    diagnosis: str
    notes: str = ""
    prescriptions: List[PrescriptionItem] = field(default_factory=list)
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_prescription(self, item: PrescriptionItem) -> None:
        self.prescriptions.append(item)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "diagnosis": self.diagnosis,
            "notes": self.notes,
            "prescriptions": [item.to_dict() for item in self.prescriptions],
            "created_at": self.created_at,
        }
