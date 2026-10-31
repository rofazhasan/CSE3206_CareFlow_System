import tempfile
import pytest
from careflow.patterns.singleton import DatabaseManager
from careflow.models.user import User, UserRole
from careflow.models.appointment import Appointment, AppointmentStatus
from careflow.models.invoice import Invoice, PaymentStatus
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.repositories.user_repository import UserRepository
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.repositories.billing_repository import BillingRepository
from careflow.repositories.medical_record_repository import MedicalRecordRepository
from careflow.services.auth_service import AuthService
from careflow.services.appointment_service import AppointmentService
from careflow.services.billing_service import BillingService
from careflow.services.medical_record_service import MedicalRecordService
from careflow.patterns.strategy import StudentDiscountStrategy, EmergencyCareStrategy
from careflow.patterns.adapter import BkashPaymentAdapter, StripePaymentAdapter
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


def test_repository_crud_integration(test_db):
    user_repo = UserRepository(test_db)
    appt_repo = AppointmentRepository(test_db)
    bill_repo = BillingRepository(test_db)
    rec_repo = MedicalRecordRepository(test_db)

    # 1. User CRUD
    pwd_hash = User.hash_password("Pass1234")
    patient = User(
        name="Rafiu Patient",
        email="rafiu.p@ruet.ac.bd",
        role=UserRole.PATIENT,
        password_hash=pwd_hash,
        phone="01711223344",
    )
    user_repo.create(patient)

    fetched_p = user_repo.get_by_email("rafiu.p@ruet.ac.bd")
    assert fetched_p is not None
    assert fetched_p.name == "Rafiu Patient"

    doctor = User(
        name="Dr. Monir",
        email="monir@ruet.ac.bd",
        role=UserRole.DOCTOR,
        password_hash=pwd_hash,
        phone="01799887766",
    )
    user_repo.create(doctor)
    doctors = user_repo.list_by_role(UserRole.DOCTOR)
    assert len(doctors) == 1

    # 2. Appointment CRUD & Slot Collision
    slot_time = "2026-11-25T10:00:00"
    assert appt_repo.is_doctor_slot_occupied(doctor.user_id, slot_time) is False

    appt = Appointment(
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        scheduled_time=slot_time,
        reason="Chest discomfort",
        fee=1200.0,
    )
    appt_repo.create(appt)
    assert appt_repo.is_doctor_slot_occupied(doctor.user_id, slot_time) is True

    # 3. Billing CRUD
    inv = Invoice(
        appointment_id=appt.appointment_id,
        patient_id=patient.user_id,
        base_amount=1200.0,
        discount_amount=360.0,
        tax_amount=0.0,
    )
    bill_repo.create_invoice(inv)
    fetched_inv = bill_repo.get_by_appointment_id(appt.appointment_id)
    assert fetched_inv is not None
    assert fetched_inv.total_payable == 840.0

    bill_repo.update_payment(inv.invoice_id, PaymentStatus.PAID, "BKASH-TEST-12345")
    updated_inv = bill_repo.get_by_id(inv.invoice_id)
    assert updated_inv.status == PaymentStatus.PAID
    assert updated_inv.payment_reference == "BKASH-TEST-12345"

    # 4. Medical Record CRUD
    rec = MedicalRecord(
        appointment_id=appt.appointment_id,
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        diagnosis="Musculoskeletal pain",
        notes="Take adequate rest and stretching.",
    )
    rec.add_prescription(PrescriptionItem("Naproxen", "250mg", "1-0-1", 5))
    rec_repo.create(rec)

    fetched_rec = rec_repo.get_by_appointment_id(appt.appointment_id)
    assert fetched_rec is not None
    assert fetched_rec.diagnosis == "Musculoskeletal pain"
    assert len(fetched_rec.prescriptions) == 1
    assert fetched_rec.prescriptions[0].medicine_name == "Naproxen"


def test_full_clinic_system_workflow_end_to_end(test_db):
    """
    Comprehensive integration test verifying the entire clinic flow:
    1. Register Patient & Doctor
    2. Register Observers to Appointment Subject
    3. Book Appointment (validating slot & notifying observers)
    4. Confirm Appointment
    5. Generate Invoice with RUET Student Subsidy Strategy
    6. Settle Invoice via bKash Adapter
    7. Doctor conducts consultation, issues prescription & completes appointment
    8. Verify Persistent Audit Trail in SQLite
    """
    user_repo = UserRepository(test_db)
    appt_repo = AppointmentRepository(test_db)
    bill_repo = BillingRepository(test_db)
    rec_repo = MedicalRecordRepository(test_db)

    # 1. Auth Service
    auth = AuthService(user_repo)
    doctor = auth.register_user("Dr. Farhana", "farhana@ruet.ac.bd", "DoctorSecurePass", UserRole.DOCTOR, "01711223344")
    patient = auth.register_user("Tahmid", "tahmid@ruet.ac.bd", "StudentPass123", UserRole.PATIENT, "01811223344")

    # 2. Appointment Observers Setup
    subject = AppointmentSubject()
    email_observer = EmailNotificationObserver()
    sms_observer = SMSNotificationObserver()
    audit_observer = AuditLogObserver(test_db)
    subject.attach(email_observer)
    subject.attach(sms_observer)
    subject.attach(audit_observer)

    appt_service = AppointmentService(appt_repo, user_repo, subject)

    # 3. Book Appointment
    slot = "2026-11-28T11:00:00"
    appt = appt_service.book_appointment(
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        scheduled_time=slot,
        reason="Migraine headache and nausea",
        fee=1000.0,
    )
    assert appt.status == AppointmentStatus.PENDING
    assert len(email_observer.sent_emails) == 1
    assert len(sms_observer.sent_sms) == 1

    # 4. Confirm Appointment
    confirmed_appt = appt_service.confirm_appointment(appt.appointment_id)
    assert confirmed_appt.status == AppointmentStatus.CONFIRMED

    # 5. Billing Service with Student Discount Strategy
    billing_service = BillingService(bill_repo, appt_repo, BkashPaymentAdapter())
    invoice = billing_service.generate_invoice(
        appointment_id=appt.appointment_id,
        strategy=StudentDiscountStrategy(),
    )
    assert invoice.base_amount == 1000.0
    assert invoice.discount_amount == 300.0
    assert invoice.total_payable == 700.0

    # 6. Settle Payment via bKash Adapter
    payment_result = billing_service.process_invoice_payment(
        invoice_id=invoice.invoice_id,
        customer_info={"phone": "01811223344"},
    )
    assert payment_result.success is True
    assert payment_result.amount_paid == 700.0
    assert payment_result.currency == "BDT"

    refreshed_inv = billing_service.get_invoice(invoice.invoice_id)
    assert refreshed_inv.status == PaymentStatus.PAID

    # 7. Medical Record & Prescription Service
    record_service = MedicalRecordService(rec_repo, appt_repo)
    rx1 = PrescriptionItem(medicine_name="Flunarizine", dosage="10mg", frequency="0-0-1 at night", duration_days=14)
    record = record_service.create_record(
        appointment_id=appt.appointment_id,
        diagnosis="Common Migraine without Aura",
        notes="Avoid sleep deprivation and bright flashing screens.",
        prescriptions=[rx1],
    )
    assert record.diagnosis == "Common Migraine without Aura"

    # Appointment should now be COMPLETED
    final_appt = appt_repo.get_by_id(appt.appointment_id)
    assert final_appt.status == AppointmentStatus.COMPLETED

    # 8. Verify Persistent SQLite Audit Trail
    conn = test_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY log_id ASC")
    logs = cursor.fetchall()
    assert len(logs) >= 2  # BOOKED and CONFIRMED logged
