import uuid
from datetime import datetime
from typing import List


class PrescriptionItem:
    def __init__(self, medicine_name: str, dosage: str, frequency: str, duration_days: int):
        self.medicine_name = medicine_name
        self.dosage = dosage  # e.g., "500mg"
        self.frequency = frequency  # e.g., "1-0-1"
        self.duration_days = int(duration_days)

    def to_dict(self) -> dict:
        return {
            "medicine_name": self.medicine_name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "duration_days": self.duration_days,
        }


class MedicalRecord:
    def __init__(self, appointment_id: str, patient_id: str, doctor_id: str, diagnosis: str, notes: str = "", prescriptions: List[PrescriptionItem] = None, record_id: str = None, created_at: str = None):
        self.record_id = record_id or str(uuid.uuid4())[:8]
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.diagnosis = diagnosis
        self.notes = notes
        self.prescriptions = prescriptions or []
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M")

    def add_prescription(self, item: PrescriptionItem):
        self.prescriptions.append(item)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "diagnosis": self.diagnosis,
            "notes": self.notes,
            "prescriptions": [p.to_dict() for p in self.prescriptions],
            "created_at": self.created_at,
        }
