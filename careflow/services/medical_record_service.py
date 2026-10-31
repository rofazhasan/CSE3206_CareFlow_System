from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.repositories.medical_record_repository import MedicalRecordRepository
from careflow.repositories.appointment_repository import AppointmentRepository


class MedicalRecordService:
    def __init__(self, record_repo=None, appointment_repo=None):
        self.record_repo = record_repo or MedicalRecordRepository()
        self.appointment_repo = appointment_repo or AppointmentRepository()

    def create_record(self, appointment_id: str, diagnosis: str, notes: str = "", prescriptions=None) -> MedicalRecord:
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

        if appt.status == "CONFIRMED":
            self.appointment_repo.update_status(appointment_id, "COMPLETED")

        return saved

    def get_patient_history(self, patient_id: str):
        return self.record_repo.list_by_patient(patient_id)
