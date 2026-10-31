"""
Observer Pattern (Behavioral Category).
Maintains a one-to-many dependency between the Appointment state subject and
observers (Email, SMS, AuditLog) so that whenever an appointment changes state,
all dependents are notified automatically.

Problem Solved:
  Tight coupling between domain state changes and external communication/auditing logic.
  Without Observer, every appointment method (book, confirm, cancel) must explicitly call
  email dispatch, SMS dispatch, and database audit inserts.

Alternative Rejected:
  Direct Sequential Method Invocations:
  - If a new observer (e.g. mobile push notification, metrics counter) is introduced,
    core domain code must be modified, violating SRP and OCP.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from careflow.models.appointment import Appointment
from careflow.patterns.singleton import DatabaseManager
from datetime import datetime


class IAppointmentObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, appointment: Appointment, metadata: Dict[str, Any]) -> None:
        """Receive state notification from appointment subject."""
        pass


class AppointmentSubject:
    """Subject/Publisher maintaining list of registered observers."""

    def __init__(self):
        self._observers: List[IAppointmentObserver] = []

    def attach(self, observer: IAppointmentObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IAppointmentObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, appointment: Appointment, metadata: Dict[str, Any] = None) -> None:
        meta = metadata or {}
        for observer in self._observers:
            observer.update(event_type, appointment, meta)


class EmailNotificationObserver(IAppointmentObserver):
    """Observer that dispatches simulated email notifications upon appointment events."""

    def __init__(self):
        self.sent_emails: List[Dict[str, Any]] = []

    def update(self, event_type: str, appointment: Appointment, metadata: Dict[str, Any]) -> None:
        recipient = metadata.get("patient_email", "patient@clinic.org")
        subject = f"CareFlow Update: Appointment {event_type}"
        message = (
            f"Dear Patient, your appointment (ID: {appointment.appointment_id[:8]}) "
            f"has been updated to {appointment.status.value}. Scheduled time: {appointment.scheduled_time}."
        )
        record = {
            "channel": "EMAIL",
            "recipient": recipient,
            "subject": subject,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.sent_emails.append(record)


class SMSNotificationObserver(IAppointmentObserver):
    """Observer that dispatches SMS alerts for critical appointment updates."""

    def __init__(self):
        self.sent_sms: List[Dict[str, Any]] = []

    def update(self, event_type: str, appointment: Appointment, metadata: Dict[str, Any]) -> None:
        phone = metadata.get("patient_phone", "+8801700000000")
        msg = f"[CareFlow] Appt {appointment.appointment_id[:8]} status: {appointment.status.value}"
        record = {
            "channel": "SMS",
            "phone": phone,
            "body": msg,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.sent_sms.append(record)


class AuditLogObserver(IAppointmentObserver):
    """Observer that records audit trails directly into persistent SQLite audit table."""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()

    def update(self, event_type: str, appointment: Appointment, metadata: Dict[str, Any]) -> None:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (event_type, entity_id, details, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                f"APPOINTMENT_{event_type.upper()}",
                appointment.appointment_id,
                f"Status changed to {appointment.status.value}. Reason: {appointment.reason}",
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
