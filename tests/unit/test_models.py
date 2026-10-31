import pytest
from careflow.models.user import User, UserRole
from careflow.models.appointment import Appointment, AppointmentStatus
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.models.invoice import Invoice, PaymentStatus


def test_user_creation_and_password_hashing():
    pwd = "SecretPassword123"
    hashed = User.hash_password(pwd)
    user = User(
        email="patient@ruet.ac.bd",
        name="Rafiu Hasan",
        role=UserRole.PATIENT,
        password_hash=hashed,
        phone="+8801700000000",
    )
    assert user.verify_password("SecretPassword123") is True
    assert user.verify_password("WrongPassword") is False
    assert user.to_dict()["role"] == "PATIENT"


def test_appointment_lifecycle():
    app = Appointment(
        patient_id="p-001",
        doctor_id="d-001",
        scheduled_time="2026-11-01T10:00:00",
        reason="Routine Checkup",
        fee=1200.0,
    )
    assert app.status == AppointmentStatus.PENDING

    app.confirm()
    assert app.status == AppointmentStatus.CONFIRMED

    app.complete()
    assert app.status == AppointmentStatus.COMPLETED

    # Cannot cancel a completed appointment
    with pytest.raises(ValueError, match="Cannot cancel an already completed appointment"):
        app.cancel()


def test_appointment_cancel_lifecycle():
    app = Appointment(
        patient_id="p-001",
        doctor_id="d-001",
        scheduled_time="2026-11-01T10:00:00",
        reason="Routine Checkup",
    )
    app.cancel()
    assert app.status == AppointmentStatus.CANCELLED

    # Cannot confirm a cancelled appointment
    with pytest.raises(ValueError, match="Cannot confirm a cancelled appointment"):
        app.confirm()


def test_medical_record_with_prescriptions():
    record = MedicalRecord(
        appointment_id="app-1",
        patient_id="p-1",
        doctor_id="d-1",
        diagnosis="Acute Bronchitis",
        notes="Patient advised to rest and stay hydrated.",
    )
    item = PrescriptionItem(
        medicine_name="Amoxicillin",
        dosage="500mg",
        frequency="1-0-1 after food",
        duration_days=7,
    )
    record.add_prescription(item)

    data = record.to_dict()
    assert len(data["prescriptions"]) == 1
    assert data["prescriptions"][0]["medicine_name"] == "Amoxicillin"


def test_invoice_calculation_and_payment():
    inv = Invoice(
        appointment_id="app-1",
        patient_id="p-1",
        base_amount=1000.0,
        discount_amount=200.0,
        tax_amount=50.0,
    )
    assert inv.total_payable == 850.0
    assert inv.status == PaymentStatus.UNPAID

    inv.mark_as_paid(reference_id="BKASH-TRX-98214")
    assert inv.status == PaymentStatus.PAID
    assert inv.payment_reference == "BKASH-TRX-98214"
