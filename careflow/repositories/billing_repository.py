from typing import Optional, List
from careflow.models.invoice import Invoice, PaymentStatus
from careflow.patterns.singleton import DatabaseManager


class BillingRepository:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create_invoice(self, invoice: Invoice) -> Invoice:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO invoices (
                invoice_id, appointment_id, patient_id, base_amount, discount_amount,
                tax_amount, total_payable, status, payment_reference, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invoice.invoice_id,
                invoice.appointment_id,
                invoice.patient_id,
                invoice.base_amount,
                invoice.discount_amount,
                invoice.tax_amount,
                invoice.total_payable,
                invoice.status.value if isinstance(invoice.status, PaymentStatus) else str(invoice.status),
                invoice.payment_reference,
                invoice.created_at,
            ),
        )
        conn.commit()
        return invoice

    def get_by_id(self, invoice_id: str) -> Optional[Invoice]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE invoice_id = ?", (invoice_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Invoice(
            invoice_id=row["invoice_id"],
            appointment_id=row["appointment_id"],
            patient_id=row["patient_id"],
            base_amount=row["base_amount"],
            discount_amount=row["discount_amount"],
            tax_amount=row["tax_amount"],
            status=PaymentStatus(row["status"]),
            payment_reference=row["payment_reference"] or "",
            created_at=row["created_at"],
        )

    def get_by_appointment_id(self, appointment_id: str) -> Optional[Invoice]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE appointment_id = ?", (appointment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Invoice(
            invoice_id=row["invoice_id"],
            appointment_id=row["appointment_id"],
            patient_id=row["patient_id"],
            base_amount=row["base_amount"],
            discount_amount=row["discount_amount"],
            tax_amount=row["tax_amount"],
            status=PaymentStatus(row["status"]),
            payment_reference=row["payment_reference"] or "",
            created_at=row["created_at"],
        )

    def update_payment(self, invoice_id: str, status: PaymentStatus, reference: str) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE invoices SET status = ?, payment_reference = ? WHERE invoice_id = ?
            """,
            (status.value, reference, invoice_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def list_by_patient(self, patient_id: str) -> List[Invoice]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
        rows = cursor.fetchall()
        return [
            Invoice(
                invoice_id=r["invoice_id"],
                appointment_id=r["appointment_id"],
                patient_id=r["patient_id"],
                base_amount=r["base_amount"],
                discount_amount=r["discount_amount"],
                tax_amount=r["tax_amount"],
                status=PaymentStatus(r["status"]),
                payment_reference=r["payment_reference"] or "",
                created_at=r["created_at"],
            )
            for r in rows
        ]
