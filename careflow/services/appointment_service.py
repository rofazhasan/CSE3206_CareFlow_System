from typing import Optional, List, Dict, Any
from careflow.models.appointment import Appointment, AppointmentStatus
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.repositories.user_repository import UserRepository
from careflow.patterns.observer import AppointmentSubject


class AppointmentService:
    def __init__(
        self,
        appointment_repo: Optional[AppointmentRepository] = None,
        user_repo: Optional[UserRepository] = None,
        subject: Optional[AppointmentSubject] = None,
    ):
        self.appointment_repo = appointment_repo or AppointmentRepository()
        self.user_repo = user_repo or UserRepository()
        self.subject = subject or AppointmentSubject()

    def book_appointment(
        self,
        patient_id: str,
        doctor_id: str,
        scheduled_time: str,
        reason: str,
        fee: float = 1000.0,
    ) -> Appointment:
        if not scheduled_time:
            raise ValueError("Scheduled appointment time must be provided.")
        if fee <= 0:
            raise ValueError("Consultation fee must be positive.")

        # Verify doctor exists and has role DOCTOR if user_repo has real users
        doctor = self.user_repo.get_by_id(doctor_id)
        if doctor and doctor.role.value != "DOCTOR":
            raise ValueError(f"User {doctor_id} is not registered as a DOCTOR.")

        # Slot conflict validation
        if self.appointment_repo.is_doctor_slot_occupied(doctor_id, scheduled_time):
            raise ValueError(f"Doctor is already booked for time slot '{scheduled_time}'. Please select another slot.")

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            scheduled_time=scheduled_time,
            reason=reason,
            fee=fee,
            status=AppointmentStatus.PENDING,
        )
        saved = self.appointment_repo.create(appointment)

        # Notify observers
        patient = self.user_repo.get_by_id(patient_id)
        meta = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "+8801700000000",
        }
        self.subject.notify("BOOKED", saved, meta)
        return saved

    def confirm_appointment(self, appointment_id: str) -> Appointment:
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with ID '{appointment_id}' not found.")
        appt.confirm()
        self.appointment_repo.update_status(appointment_id, appt.status)

        patient = self.user_repo.get_by_id(appt.patient_id)
        meta = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "+8801700000000",
        }
        self.subject.notify("CONFIRMED", appt, meta)
        return appt

    def complete_appointment(self, appointment_id: str) -> Appointment:
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with ID '{appointment_id}' not found.")
        appt.complete()
        self.appointment_repo.update_status(appointment_id, appt.status)

        patient = self.user_repo.get_by_id(appt.patient_id)
        meta = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "+8801700000000",
        }
        self.subject.notify("COMPLETED", appt, meta)
        return appt

    def cancel_appointment(self, appointment_id: str, cancellation_reason: str = "") -> Appointment:
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with ID '{appointment_id}' not found.")
        appt.cancel()
        self.appointment_repo.update_status(appointment_id, appt.status)

        patient = self.user_repo.get_by_id(appt.patient_id)
        meta = {
            "patient_email": patient.email if patient else "patient@careflow.org",
            "patient_phone": patient.phone if patient else "+8801700000000",
            "cancellation_reason": cancellation_reason,
        }
        self.subject.notify("CANCELLED", appt, meta)
        return appt

    def get_patient_appointments(self, patient_id: str) -> List[Appointment]:
        return self.appointment_repo.list_by_patient(patient_id)

    def get_doctor_appointments(self, doctor_id: str) -> List[Appointment]:
        return self.appointment_repo.list_by_doctor(doctor_id)
