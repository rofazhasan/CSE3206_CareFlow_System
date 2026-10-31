from typing import Optional, List
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.models.appointment import AppointmentStatus
from careflow.repositories.medical_record_repository import MedicalRecordRepository
from careflow.repositories.appointment_repository import AppointmentRepository


class MedicalRecordService:
    def __init__(
        self,
        record_repo: Optional[MedicalRecordRepository] = None,
        appointment_repo: Optional[AppointmentRepository] = None,
    ):
        self.record_repo = record_repo or MedicalRecordRepository()
        self.appointment_repo = appointment_repo or AppointmentRepository()

    def create_record(
        self,
        appointment_id: str,
        diagnosis: str,
        notes: str = "",
        prescriptions: Optional[List[PrescriptionItem]] = None,
    ) -> MedicalRecord:
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with ID '{appointment_id}' does not exist.")

        if not diagnosis.strip():
            raise ValueError("Clinical diagnosis cannot be empty.")

        existing = self.record_repo.get_by_appointment_id(appointment_id)
        if existing:
            raise ValueError(f"Medical record already exists for appointment '{appointment_id}'.")

        record = MedicalRecord(
            appointment_id=appointment_id,
            patient_id=appt.patient_id,
            doctor_id=appt.doctor_id,
            diagnosis=diagnosis.strip(),
            notes=notes.strip(),
            prescriptions=prescriptions or [],
        )
        saved = self.record_repo.create(record)

        # Mark appointment as completed upon diagnosis submission if it was confirmed
        if appt.status == AppointmentStatus.CONFIRMED:
            self.appointment_repo.update_status(appointment_id, AppointmentStatus.COMPLETED)

        return saved

    def get_patient_history(self, patient_id: str) -> List[MedicalRecord]:
        return self.record_repo.list_by_patient(patient_id)

    def get_record_by_appointment(self, appointment_id: str) -> Optional[MedicalRecord]:
        return self.record_repo.get_by_appointment_id(appointment_id)
