import pytest
from careflow.models.user import User
from careflow.models.appointment import Appointment
from careflow.models.medical_record import MedicalRecord, PrescriptionItem
from careflow.models.invoice import Invoice


def test_user_creation_and_password_hashing():
    pwd = "MySecretPassword"
    hashed = User.hash_password(pwd)
    user = User(name="Rafiu", email="rafiu@ruet.ac.bd", role="PATIENT", password_hash=hashed, phone="01711223344")
    assert user.verify_password("MySecretPassword") is True
    assert user.verify_password("WrongPassword") is False
    assert user.role == "PATIENT"


def test_appointment_lifecycle():
    appt = Appointment(patient_id="p1", doctor_id="d1", scheduled_time="2026-11-20 10:00", reason="Checkup", fee=1000.0)
    assert appt.status == "PENDING"

    appt.confirm()
    assert appt.status == "CONFIRMED"

    appt.complete()
    assert appt.status == "COMPLETED"

    # Cannot cancel completed appointment
    with pytest.raises(ValueError):
        appt.cancel()


def test_appointment_cancel():
    appt = Appointment(patient_id="p1", doctor_id="d1", scheduled_time="2026-11-20 10:00", reason="Checkup")
    appt.cancel()
    assert appt.status == "CANCELLED"

    # Cannot confirm cancelled appointment
    with pytest.raises(ValueError):
        appt.confirm()


def test_medical_record_with_prescriptions():
    record = MedicalRecord(appointment_id="a1", patient_id="p1", doctor_id="d1", diagnosis="Common Cold")
    item = PrescriptionItem(medicine_name="Paracetamol", dosage="500mg", frequency="1-0-1", duration_days=3)
    record.add_prescription(item)

    data = record.to_dict()
    assert data["diagnosis"] == "Common Cold"
    assert len(data["prescriptions"]) == 1
    assert data["prescriptions"][0]["medicine_name"] == "Paracetamol"


def test_invoice_calculation_and_payment():
    inv = Invoice(appointment_id="a1", patient_id="p1", base_amount=1000.0, discount_amount=300.0, tax_amount=50.0)
    assert inv.total_payable == 750.0
    assert inv.status == "UNPAID"

    inv.mark_as_paid("BKASH-12345")
    assert inv.status == "PAID"
    assert inv.payment_reference == "BKASH-12345"
