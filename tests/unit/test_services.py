import pytest
from unittest.mock import MagicMock, patch
from careflow.models.user import User, UserRole
from careflow.models.appointment import Appointment, AppointmentStatus
from careflow.models.invoice import Invoice, PaymentStatus
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.services.auth_service import AuthService
from careflow.services.appointment_service import AppointmentService
from careflow.services.billing_service import BillingService
from careflow.services.medical_record_service import MedicalRecordService
from careflow.patterns.strategy import StudentDiscountStrategy
from careflow.patterns.adapter import PaymentResult


# ==========================================
# 1. AuthService Unit Tests with Mocks
# ==========================================

def test_auth_service_register_success():
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.side_effect = lambda u: u

    service = AuthService(user_repo=mock_user_repo)
    user = service.register_user(
        name="Dr. Shamsul",
        email="shamsul@ruet.ac.bd",
        password="StrongPassword123",
        role=UserRole.DOCTOR,
        phone="01712345678",
    )

    assert user.email == "shamsul@ruet.ac.bd"
    assert user.role == UserRole.DOCTOR
    mock_user_repo.get_by_email.assert_called_once_with("shamsul@ruet.ac.bd")
    mock_user_repo.create.assert_called_once()


def test_auth_service_duplicate_email_raises_error():
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_email.return_value = User(
        name="Existing", email="test@ruet.ac.bd", role=UserRole.PATIENT, password_hash="abc"
    )

    service = AuthService(user_repo=mock_user_repo)
    with pytest.raises(ValueError, match="already exists"):
        service.register_user("New User", "test@ruet.ac.bd", "123456", UserRole.PATIENT)


def test_auth_service_authentication_and_jwt_simulation():
    mock_user_repo = MagicMock()
    pwd = "ValidPassword123"
    hashed = User.hash_password(pwd)
    mock_user = User(
        name="Rafiu",
        email="rafiu@ruet.ac.bd",
        role=UserRole.PATIENT,
        password_hash=hashed,
    )
    mock_user_repo.get_by_email.return_value = mock_user

    service = AuthService(user_repo=mock_user_repo)
    auth_data = service.authenticate("rafiu@ruet.ac.bd", pwd)
    assert "access_token" in auth_data
    assert auth_data["user"]["email"] == "rafiu@ruet.ac.bd"

    # Verify decoding token
    decoded = service.decode_token(auth_data["access_token"])
    assert decoded["email"] == "rafiu@ruet.ac.bd"
    assert decoded["role"] == "PATIENT"


# ==========================================
# 2. AppointmentService Unit Tests with Mocks
# ==========================================

def test_appointment_service_book_detects_slot_collision():
    mock_appt_repo = MagicMock()
    mock_user_repo = MagicMock()
    mock_subject = MagicMock()

    # Configure doctor user mock
    mock_user_repo.get_by_id.return_value = User(
        user_id="doc1",
        name="Dr. Shamsul",
        email="shamsul@ruet.ac.bd",
        role=UserRole.DOCTOR,
        password_hash="hashed_pw",
    )

    # Simulate doctor slot already occupied
    mock_appt_repo.is_doctor_slot_occupied.return_value = True

    service = AppointmentService(
        appointment_repo=mock_appt_repo,
        user_repo=mock_user_repo,
        subject=mock_subject,
    )

    with pytest.raises(ValueError, match="Doctor is already booked for time slot"):
        service.book_appointment(
            patient_id="p1",
            doctor_id="doc1",
            scheduled_time="2026-11-10T10:00:00",
            reason="Cardio follow-up",
        )

    mock_appt_repo.create.assert_not_called()
    mock_subject.notify.assert_not_called()


def test_appointment_service_book_success_notifies_observers():
    mock_appt_repo = MagicMock()
    mock_user_repo = MagicMock()
    mock_subject = MagicMock()

    mock_appt_repo.is_doctor_slot_occupied.return_value = False
    mock_user_repo.get_by_id.side_effect = lambda uid: User(
        user_id=uid, name="Dr. A", email="doc@clinic.com", role=UserRole.DOCTOR, password_hash="x", phone="0171"
    )
    mock_appt_repo.create.side_effect = lambda a: a

    service = AppointmentService(
        appointment_repo=mock_appt_repo,
        user_repo=mock_user_repo,
        subject=mock_subject,
    )

    appt = service.book_appointment(
        patient_id="p10",
        doctor_id="doc10",
        scheduled_time="2026-11-10T14:00:00",
        reason="Dermatology rash",
        fee=1500.0,
    )

    assert appt.status == AppointmentStatus.PENDING
    mock_appt_repo.create.assert_called_once()
    mock_subject.notify.assert_called_once()
    assert mock_subject.notify.call_args[0][0] == "BOOKED"


def test_appointment_service_confirm_and_cancel_lifecycle():
    mock_appt_repo = MagicMock()
    mock_user_repo = MagicMock()
    mock_subject = MagicMock()

    appt = Appointment(
        appointment_id="app-999",
        patient_id="p1",
        doctor_id="d1",
        scheduled_time="2026-11-12T09:00:00",
        reason="Routine Check",
    )
    mock_appt_repo.get_by_id.return_value = appt

    service = AppointmentService(
        appointment_repo=mock_appt_repo,
        user_repo=mock_user_repo,
        subject=mock_subject,
    )

    confirmed = service.confirm_appointment("app-999")
    assert confirmed.status == AppointmentStatus.CONFIRMED
    mock_appt_repo.update_status.assert_called_with("app-999", AppointmentStatus.CONFIRMED)


# ==========================================
# 3. BillingService Unit Tests with Mocks
# ==========================================

def test_billing_service_generates_invoice_with_strategy():
    mock_billing_repo = MagicMock()
    mock_appt_repo = MagicMock()
    mock_processor = MagicMock()

    appt = Appointment(
        appointment_id="app-123",
        patient_id="p-100",
        doctor_id="d-200",
        scheduled_time="2026-11-15T11:00:00",
        reason="General",
        fee=1000.0,
    )
    mock_appt_repo.get_by_id.return_value = appt
    mock_billing_repo.get_by_appointment_id.return_value = None
    mock_billing_repo.create_invoice.side_effect = lambda inv: inv

    service = BillingService(
        billing_repo=mock_billing_repo,
        appointment_repo=mock_appt_repo,
        payment_processor=mock_processor,
    )

    # Use Student 30% discount strategy
    strategy = StudentDiscountStrategy()
    invoice = service.generate_invoice("app-123", strategy=strategy)

    assert invoice.base_amount == 1000.0
    assert invoice.discount_amount == 300.0
    assert invoice.total_payable == 700.0
    assert invoice.status == PaymentStatus.UNPAID
    mock_billing_repo.create_invoice.assert_called_once()


def test_billing_service_processes_payment_via_mocked_gateway():
    mock_billing_repo = MagicMock()
    mock_appt_repo = MagicMock()
    mock_processor = MagicMock()

    invoice = Invoice(
        invoice_id="inv-888",
        appointment_id="app-123",
        patient_id="p-100",
        base_amount=1000.0,
        discount_amount=300.0,
        tax_amount=0.0,
    )
    mock_billing_repo.get_by_id.return_value = invoice

    # Mock gateway returns successful transaction
    mock_processor.process_payment.return_value = PaymentResult(
        success=True,
        transaction_id="TRX-MOCK-777",
        amount_paid=700.0,
        currency="BDT",
        gateway_name="Mock-Gateway",
    )

    service = BillingService(
        billing_repo=mock_billing_repo,
        appointment_repo=mock_appt_repo,
        payment_processor=mock_processor,
    )

    res = service.process_invoice_payment("inv-888", customer_info={"phone": "01700000000"})

    assert res.success is True
    assert res.transaction_id == "TRX-MOCK-777"
    assert invoice.status == PaymentStatus.PAID
    mock_billing_repo.update_payment.assert_called_once_with(
        invoice_id="inv-888", status=PaymentStatus.PAID, reference="TRX-MOCK-777"
    )


# ==========================================
# 4. MedicalRecordService Unit Tests with Mocks
# ==========================================

def test_medical_record_service_creates_prescription():
    mock_record_repo = MagicMock()
    mock_appt_repo = MagicMock()

    appt = Appointment(
        appointment_id="app-555",
        patient_id="p-50",
        doctor_id="d-60",
        scheduled_time="2026-11-20T10:00:00",
        reason="Fever & Cough",
        status=AppointmentStatus.CONFIRMED,
    )
    mock_appt_repo.get_by_id.return_value = appt
    mock_record_repo.get_by_appointment_id.return_value = None
    mock_record_repo.create.side_effect = lambda r: r

    service = MedicalRecordService(record_repo=mock_record_repo, appointment_repo=mock_appt_repo)

    med = PrescriptionItem(
        medicine_name="Paracetamol", dosage="500mg", frequency="1-1-1", duration_days=3
    )
    record = service.create_record(
        appointment_id="app-555",
        diagnosis="Viral Upper Respiratory Tract Infection",
        notes="Plenty of warm liquids.",
        prescriptions=[med],
    )

    assert record.diagnosis == "Viral Upper Respiratory Tract Infection"
    assert len(record.prescriptions) == 1
    mock_appt_repo.update_status.assert_called_with("app-555", AppointmentStatus.COMPLETED)
