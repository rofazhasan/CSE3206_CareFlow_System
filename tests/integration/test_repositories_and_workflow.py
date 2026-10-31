import tempfile
import pytest
from careflow.patterns.singleton import DatabaseManager
from careflow.models.user import User
from careflow.models.appointment import Appointment
from careflow.models.invoice import Invoice
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.repositories.user_repository import UserRepository
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.repositories.billing_repository import BillingRepository
from careflow.repositories.medical_record_repository import MedicalRecordRepository
from careflow.services.auth_service import AuthService
from careflow.services.appointment_service import AppointmentService
from careflow.services.billing_service import BillingService
from careflow.services.medical_record_service import MedicalRecordService
from careflow.patterns.strategy import StudentDiscountStrategy
from careflow.patterns.adapter import BkashPaymentAdapter
from careflow.patterns.observer import (
    AppointmentSubject,
    EmailNotificationObserver,
    SMSNotificationObserver,
    AuditLogObserver,
)


@pytest.fixture
def test_db():
    DatabaseManager.reset_instance()
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db = DatabaseManager(tmp.name)
        yield db
        db.close()
        DatabaseManager.reset_instance()


def test_repositories_crud(test_db):
    user_repo = UserRepository(test_db)
    appt_repo = AppointmentRepository(test_db)
    bill_repo = BillingRepository(test_db)
    rec_repo = MedicalRecordRepository(test_db)

    # User
    u = User("Test User", "test@ruet.ac.bd", "PATIENT", "hash", "01711223344")
    user_repo.create(u)
    fetched_u = user_repo.get_by_email("test@ruet.ac.bd")
    assert fetched_u is not None
    assert fetched_u.name == "Test User"

    # Appointment
    appt = Appointment(u.user_id, "doc1", "2026-11-20 10:00", "Headache", 1000.0)
    appt_repo.create(appt)
    assert appt_repo.is_doctor_slot_occupied("doc1", "2026-11-20 10:00") is True

    # Billing
    inv = Invoice(appt.appointment_id, u.user_id, 1000.0, 300.0, 0.0)
    bill_repo.create_invoice(inv)
    fetched_inv = bill_repo.get_by_appointment_id(appt.appointment_id)
    assert fetched_inv is not None
    assert fetched_inv.total_payable == 700.0

    # Medical Record
    rec = MedicalRecord(appt.appointment_id, u.user_id, "doc1", "Tension Headache")
    rec.add_prescription(PrescriptionItem("Aspirin", "100mg", "1-0-0", 5))
    rec_repo.create(rec)
    fetched_rec = rec_repo.get_by_appointment_id(appt.appointment_id)
    assert fetched_rec is not None
    assert len(fetched_rec.prescriptions) == 1


def test_full_clinic_workflow_end_to_end(test_db):
    user_repo = UserRepository(test_db)
    appt_repo = AppointmentRepository(test_db)
    bill_repo = BillingRepository(test_db)
    rec_repo = MedicalRecordRepository(test_db)

    auth = AuthService(user_repo)
    doctor = auth.register_user("Dr. Rahman", "rahman@ruet.ac.bd", "Pass1234", "DOCTOR", "01711223344")
    patient = auth.register_user("Rafiu", "rafiu@ruet.ac.bd", "Pass1234", "PATIENT", "01811223344")

    subject = AppointmentSubject()
    email_obs = EmailNotificationObserver()
    sms_obs = SMSNotificationObserver()
    audit_obs = AuditLogObserver(test_db)
    subject.attach(email_obs)
    subject.attach(sms_obs)
    subject.attach(audit_obs)

    appt_service = AppointmentService(appt_repo, user_repo, subject)
    billing_service = BillingService(bill_repo, appt_repo, BkashPaymentAdapter())
    record_service = MedicalRecordService(rec_repo, appt_repo)

    # 1. Book
    appt = appt_service.book_appointment(patient.user_id, doctor.user_id, "2026-11-25 10:00", "Eye pain", 1200.0)
    assert appt.status == "PENDING"
    assert len(email_obs.sent_emails) == 1

    # 2. Confirm
    confirmed = appt_service.confirm_appointment(appt.appointment_id)
    assert confirmed.status == "CONFIRMED"

    # 3. Bill with Student Subsidy
    inv = billing_service.generate_invoice(appt.appointment_id, strategy=StudentDiscountStrategy())
    assert inv.total_payable == 840.0  # 1200 - 30% = 840

    # 4. Pay
    pay_res = billing_service.process_invoice_payment(inv.invoice_id, {"phone": patient.phone})
    assert pay_res.success is True

    # 5. Prescribe
    rx = PrescriptionItem("Eye Drop", "1 drop", "2 times", 7)
    rec = record_service.create_record(appt.appointment_id, "Dry Eyes", "Rest", [rx])
    assert rec.diagnosis == "Dry Eyes"
    assert appt_repo.get_by_id(appt.appointment_id).status == "COMPLETED"
