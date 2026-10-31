import pytest
from unittest.mock import MagicMock
from careflow.models.user import User
from careflow.models.appointment import Appointment
from careflow.models.invoice import Invoice
from careflow.models.medical_record import PrescriptionItem
from careflow.services.auth_service import AuthService
from careflow.services.appointment_service import AppointmentService
from careflow.services.billing_service import BillingService
from careflow.services.medical_record_service import MedicalRecordService
from careflow.patterns.strategy import StudentDiscountStrategy
from careflow.patterns.adapter import PaymentResult


def test_auth_service_register_and_authenticate():
    mock_repo = MagicMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create.side_effect = lambda u: u

    auth = AuthService(user_repo=mock_repo)
    user = auth.register_user("Dr. Ali", "ali@ruet.ac.bd", "Password123", "DOCTOR", "01711223344")
    assert user.email == "ali@ruet.ac.bd"
    assert user.role == "DOCTOR"

    # Authenticate
    mock_repo.get_by_email.return_value = user
    login_data = auth.authenticate("ali@ruet.ac.bd", "Password123")
    assert "access_token" in login_data
    assert login_data["user"]["email"] == "ali@ruet.ac.bd"


def test_auth_service_duplicate_email():
    mock_repo = MagicMock()
    mock_repo.get_by_email.return_value = User("Existing", "dup@ruet.ac.bd", "PATIENT", "hash")
    auth = AuthService(user_repo=mock_repo)

    with pytest.raises(ValueError, match="already exists"):
        auth.register_user("New", "dup@ruet.ac.bd", "Password123", "PATIENT")


def test_appointment_service_slot_collision():
    mock_appt_repo = MagicMock()
    mock_user_repo = MagicMock()
    mock_subject = MagicMock()

    mock_user_repo.get_by_id.return_value = User("Dr. Ali", "ali@ruet.ac.bd", "DOCTOR", "hash")
    mock_appt_repo.is_doctor_slot_occupied.return_value = True

    service = AppointmentService(mock_appt_repo, mock_user_repo, mock_subject)
    with pytest.raises(ValueError, match="Doctor is already booked for time slot"):
        service.book_appointment("p1", "doc1", "2026-11-20 10:00", "Checkup")


def test_appointment_service_booking_and_confirm():
    mock_appt_repo = MagicMock()
    mock_user_repo = MagicMock()
    mock_subject = MagicMock()

    mock_user_repo.get_by_id.return_value = User("Dr. Ali", "ali@ruet.ac.bd", "DOCTOR", "hash")
    mock_appt_repo.is_doctor_slot_occupied.return_value = False
    mock_appt_repo.create.side_effect = lambda a: a

    service = AppointmentService(mock_appt_repo, mock_user_repo, mock_subject)
    appt = service.book_appointment("p1", "doc1", "2026-11-20 10:00", "Fever", 1200.0)

    assert appt.status == "PENDING"
    mock_appt_repo.create.assert_called_once()
    mock_subject.notify.assert_called_once()

    # Confirm
    mock_appt_repo.get_by_id.return_value = appt
    confirmed = service.confirm_appointment(appt.appointment_id)
    assert confirmed.status == "CONFIRMED"


def test_billing_service_generates_invoice_with_strategy():
    mock_bill_repo = MagicMock()
    mock_appt_repo = MagicMock()
    mock_processor = MagicMock()

    appt = Appointment("p1", "doc1", "2026-11-20 10:00", "Checkup", 1000.0)
    mock_appt_repo.get_by_id.return_value = appt
    mock_bill_repo.get_by_appointment_id.return_value = None
    mock_bill_repo.create_invoice.side_effect = lambda inv: inv

    service = BillingService(mock_bill_repo, mock_appt_repo, mock_processor)
    invoice = service.generate_invoice(appt.appointment_id, strategy=StudentDiscountStrategy())

    assert invoice.base_amount == 1000.0
    assert invoice.discount_amount == 300.0
    assert invoice.total_payable == 700.0
    assert invoice.status == "UNPAID"


def test_billing_service_payment_processing():
    mock_bill_repo = MagicMock()
    mock_appt_repo = MagicMock()
    mock_processor = MagicMock()

    invoice = Invoice("a1", "p1", 1000.0, 300.0, 0.0)
    mock_bill_repo.get_by_id.return_value = invoice
    mock_processor.process_payment.return_value = PaymentResult(True, "TRX-MOCK-123", 700.0, "BDT", "MockGateway")

    service = BillingService(mock_bill_repo, mock_appt_repo, mock_processor)
    result = service.process_invoice_payment("inv-1", {"phone": "01711223344"})

    assert result.success is True
    assert result.transaction_id == "TRX-MOCK-123"
    assert invoice.status == "PAID"
    mock_bill_repo.update_payment.assert_called_once()


def test_medical_record_service():
    mock_rec_repo = MagicMock()
    mock_appt_repo = MagicMock()

    appt = Appointment("p1", "d1", "2026-11-20 10:00", "Fever", status="CONFIRMED")
    mock_appt_repo.get_by_id.return_value = appt
    mock_rec_repo.get_by_appointment_id.return_value = None
    mock_rec_repo.create.side_effect = lambda r: r

    service = MedicalRecordService(mock_rec_repo, mock_appt_repo)
    med = PrescriptionItem("Napa", "500mg", "1-0-1", 3)
    record = service.create_record(appt.appointment_id, "Viral Infection", "Rest", [med])

    assert record.diagnosis == "Viral Infection"
    assert len(record.prescriptions) == 1
    mock_appt_repo.update_status.assert_called_with(appt.appointment_id, "COMPLETED")
