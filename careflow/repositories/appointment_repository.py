from typing import Optional, List
from careflow.models.appointment import Appointment, AppointmentStatus
from careflow.patterns.singleton import DatabaseManager


class AppointmentRepository:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, appointment: Appointment) -> Appointment:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO appointments (
                appointment_id, patient_id, doctor_id, scheduled_time, reason, fee, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appointment.appointment_id,
                appointment.patient_id,
                appointment.doctor_id,
                appointment.scheduled_time,
                appointment.reason,
                appointment.fee,
                appointment.status.value if isinstance(appointment.status, AppointmentStatus) else str(appointment.status),
                appointment.created_at,
            ),
        )
        conn.commit()
        return appointment

    def get_by_id(self, appointment_id: str) -> Optional[Appointment]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE appointment_id = ?", (appointment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Appointment(
            appointment_id=row["appointment_id"],
            patient_id=row["patient_id"],
            doctor_id=row["doctor_id"],
            scheduled_time=row["scheduled_time"],
            reason=row["reason"],
            fee=row["fee"],
            status=AppointmentStatus(row["status"]),
            created_at=row["created_at"],
        )

    def is_doctor_slot_occupied(self, doctor_id: str, scheduled_time: str, exclude_appointment_id: Optional[str] = None) -> bool:
        """Checks if a doctor already has an active (non-cancelled) appointment at the specified slot."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if exclude_appointment_id:
            cursor.execute(
                """
                SELECT COUNT(*) as cnt FROM appointments
                WHERE doctor_id = ? AND scheduled_time = ? AND status != 'CANCELLED' AND appointment_id != ?
                """,
                (doctor_id, scheduled_time, exclude_appointment_id),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) as cnt FROM appointments
                WHERE doctor_id = ? AND scheduled_time = ? AND status != 'CANCELLED'
                """,
                (doctor_id, scheduled_time),
            )
        row = cursor.fetchone()
        return (row["cnt"] > 0) if row else False

    def update_status(self, appointment_id: str, status: AppointmentStatus) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE appointments SET status = ? WHERE appointment_id = ?",
            (status.value, appointment_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def list_by_patient(self, patient_id: str) -> List[Appointment]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE patient_id = ? ORDER BY scheduled_time DESC", (patient_id,))
        rows = cursor.fetchall()
        return [
            Appointment(
                appointment_id=r["appointment_id"],
                patient_id=r["patient_id"],
                doctor_id=r["doctor_id"],
                scheduled_time=r["scheduled_time"],
                reason=r["reason"],
                fee=r["fee"],
                status=AppointmentStatus(r["status"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def list_by_doctor(self, doctor_id: str) -> List[Appointment]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE doctor_id = ? ORDER BY scheduled_time ASC", (doctor_id,))
        rows = cursor.fetchall()
        return [
            Appointment(
                appointment_id=r["appointment_id"],
                patient_id=r["patient_id"],
                doctor_id=r["doctor_id"],
                scheduled_time=r["scheduled_time"],
                reason=r["reason"],
                fee=r["fee"],
                status=AppointmentStatus(r["status"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]
