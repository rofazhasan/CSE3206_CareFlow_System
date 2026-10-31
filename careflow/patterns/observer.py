"""
Observer Pattern (Behavioral Category).
Maintains a one-to-many dependency so when an appointment changes state,
all registered observers (Email, SMS, AuditLog) are notified automatically.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from careflow.patterns.singleton import DatabaseManager


class IAppointmentObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, appointment, metadata: dict):
        pass


class AppointmentSubject:
    """Subject that maintains and notifies registered observers."""
    def __init__(self):
        self._observers = []

    def attach(self, observer: IAppointmentObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IAppointmentObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, appointment, metadata: dict = None):
        meta = metadata or {}
        for observer in self._observers:
            observer.update(event_type, appointment, meta)


class EmailNotificationObserver(IAppointmentObserver):
    def __init__(self):
        self.sent_emails = []

    def update(self, event_type: str, appointment, metadata: dict):
        email = metadata.get("patient_email", "patient@clinic.org")
        msg = f"Appointment {appointment.appointment_id} is now {appointment.status}."
        self.sent_emails.append({"channel": "EMAIL", "recipient": email, "message": msg})


class SMSNotificationObserver(IAppointmentObserver):
    def __init__(self):
        self.sent_sms = []

    def update(self, event_type: str, appointment, metadata: dict):
        phone = metadata.get("patient_phone", "01700000000")
        msg = f"[CareFlow] Appt {appointment.appointment_id} status: {appointment.status}"
        self.sent_sms.append({"channel": "SMS", "phone": phone, "body": msg})


class AuditLogObserver(IAppointmentObserver):
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()

    def update(self, event_type: str, appointment, metadata: dict):
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
                f"Status: {appointment.status}, Reason: {appointment.reason}",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
        conn.commit()
