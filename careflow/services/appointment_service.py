from careflow.models.appointment import Appointment
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.repositories.user_repository import UserRepository
from careflow.patterns.observer import AppointmentSubject


class AppointmentService:
    def __init__(self, appointment_repo=None, user_repo=None, subject=None):
        self.appointment_repo = appointment_repo or AppointmentRepository()
        self.user_repo = user_repo or UserRepository()
        self.subject = subject or AppointmentSubject()

    def book_appointment(self, patient_id: str, doctor_id: str, scheduled_time: str, reason: str, fee: float = 1000.0) -> Appointment:
        if not scheduled_time:
            raise ValueError("Scheduled appointment time must be provided.")
        if fee <= 0:
            raise ValueError("Consultation fee must be positive.")

        doctor = self.user_repo.get_by_id(doctor_id)
        if doctor and doctor.role != "DOCTOR":
            raise ValueError(f"User {doctor_id} is not registered as a DOCTOR.")

        # Check if slot is already occupied
        if self.appointment_repo.is_doctor_slot_occupied(doctor_id, scheduled_time):
            raise ValueError(f"Doctor is already booked for time slot '{scheduled_time}'. Please select another slot.")

        appt = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            scheduled_time=scheduled_time,
            reason=reason,
            fee=fee,
            status="PENDING",
        )
        saved = self.appointment_repo.create(appt)

        # Notify observers
        patient = self.user_repo.get_by_id(patient_id)
        metadata = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "01700000000",
        }
        self.subject.notify("BOOKED", saved, metadata)
        return saved

    def confirm_appointment(self, appointment_id: str) -> Appointment:
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with ID '{appointment_id}' not found.")
        appt.confirm()
        self.appointment_repo.update_status(appointment_id, appt.status)

        patient = self.user_repo.get_by_id(appt.patient_id)
        metadata = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "01700000000",
        }
        self.subject.notify("CONFIRMED", appt, metadata)
        return appt

    def cancel_appointment(self, appointment_id: str, reason: str = "") -> Appointment:
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with ID '{appointment_id}' not found.")
        appt.cancel()
        self.appointment_repo.update_status(appointment_id, appt.status)

        patient = self.user_repo.get_by_id(appt.patient_id)
        metadata = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "01700000000",
            "cancel_reason": reason,
        }
        self.subject.notify("CANCELLED", appt, metadata)
        return appt
