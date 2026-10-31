import json
from typing import Optional, List
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.patterns.singleton import DatabaseManager


class MedicalRecordRepository:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, record: MedicalRecord) -> MedicalRecord:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        prescriptions_json = json.dumps([item.to_dict() for item in record.prescriptions])
        cursor.execute(
            """
            INSERT INTO medical_records (
                record_id, appointment_id, patient_id, doctor_id, diagnosis, notes, prescriptions_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.record_id,
                record.appointment_id,
                record.patient_id,
                record.doctor_id,
                record.diagnosis,
                record.notes,
                prescriptions_json,
                record.created_at,
            ),
        )
        conn.commit()
        return record

    def get_by_appointment_id(self, appointment_id: str) -> Optional[MedicalRecord]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_records WHERE appointment_id = ?", (appointment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        items_data = json.loads(row["prescriptions_json"])
        prescriptions = [PrescriptionItem(**item) for item in items_data]
        return MedicalRecord(
            record_id=row["record_id"],
            appointment_id=row["appointment_id"],
            patient_id=row["patient_id"],
            doctor_id=row["doctor_id"],
            diagnosis=row["diagnosis"],
            notes=row["notes"] or "",
            prescriptions=prescriptions,
            created_at=row["created_at"],
        )

    def list_by_patient(self, patient_id: str) -> List[MedicalRecord]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_records WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            items_data = json.loads(r["prescriptions_json"])
            prescriptions = [PrescriptionItem(**item) for item in items_data]
            results.append(
                MedicalRecord(
                    record_id=r["record_id"],
                    appointment_id=r["appointment_id"],
                    patient_id=r["patient_id"],
                    doctor_id=r["doctor_id"],
                    diagnosis=r["diagnosis"],
                    notes=r["notes"] or "",
                    prescriptions=prescriptions,
                    created_at=r["created_at"],
                )
            )
        return results
