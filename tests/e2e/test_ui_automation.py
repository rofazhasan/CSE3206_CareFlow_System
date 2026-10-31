"""
CareFlow UI / End-to-End Workflow Automation.
Verifies the complete end-to-end journey of a clinic visitor,
demonstrating automated testing principles aligned with the RUET CSE 3206 syllabus.
"""

from fastapi.testclient import TestClient
from careflow.api.app import app
import uuid

client = TestClient(app)


def test_e2e_clinic_patient_journey():
    """
    Simulates a full user journey across all 5 functional modules:
    1. Patient lands on portal (Health Check).
    2. Patient registers an account with valid credentials.
    3. Patient logs in and receives bearer token.
    4. Doctor registers and provides available schedule.
    5. Patient books appointment slot.
    6. System blocks competing booking at identical slot.
    7. Clinic staff confirms appointment.
    8. Patient views calculated bill under RUET Student Scheme (30% discount).
    9. Patient pays via bKash adapter.
    10. Doctor conducts consultation and inputs electronic prescription.
    """
    uid = uuid.uuid4().hex[:6]

    # Step 1: Health check
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["database"] == "SQLite (Singleton Pool)"

    # Step 2: Patient registration
    p_email = f"student.{uid}@ruet.ac.bd"
    p_reg = client.post(
        "/api/auth/register",
        json={
            "name": f"Student {uid}",
            "email": p_email,
            "password": "Password123!",
            "role": "PATIENT",
            "phone": "01755123456",
        },
    )
    assert p_reg.status_code == 201
    patient_id = p_reg.json()["user"]["user_id"]

    # Step 3: Login
    p_login = client.post(
        "/api/auth/login",
        json={"email": p_email, "password": "Password123!"},
    )
    assert p_login.status_code == 200
    token = p_login.json()["access_token"]
    assert len(token) > 20

    # Step 4: Doctor registration
    d_email = f"doctor.{uid}@ruet.ac.bd"
    d_reg = client.post(
        "/api/auth/register",
        json={
            "name": f"Dr. Specialist {uid}",
            "email": d_email,
            "password": "DocPass2026!",
            "role": "DOCTOR",
            "phone": "01788990011",
        },
    )
    assert d_reg.status_code == 201
    doctor_id = d_reg.json()["user"]["user_id"]

    # Step 5: Patient books appointment
    slot = f"2026-12-10T11:00:00"
    book_res = client.post(
        "/api/appointments/book",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "scheduled_time": slot,
            "reason": "Chronic headaches and eye fatigue during exam week",
            "fee": 1500.0,
        },
    )
    assert book_res.status_code == 201
    appt_id = book_res.json()["appointment"]["appointment_id"]

    # Step 6: Verify slot collision guard
    dup_res = client.post(
        "/api/appointments/book",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "scheduled_time": slot,
            "reason": "Competing second booking",
            "fee": 1500.0,
        },
    )
    assert dup_res.status_code == 400
    assert "already booked" in dup_res.json()["detail"]

    # Step 7: Confirm appointment
    conf_res = client.put(f"/api/appointments/{appt_id}/confirm")
    assert conf_res.status_code == 200

    # Step 8: Generate bill under Student Scheme (30% subsidy)
    inv_res = client.post(
        "/api/billing/generate",
        json={"appointment_id": appt_id, "scheme": "STUDENT"},
    )
    assert inv_res.status_code == 201
    inv_data = inv_res.json()["invoice"]
    # 1500 - 30% (450) = 1050
    assert inv_data["total_payable"] == 1050.0

    # Step 9: Pay via bKash
    pay_res = client.post(
        "/api/billing/pay",
        json={
            "invoice_id": inv_data["invoice_id"],
            "gateway": "BKASH",
            "phone": "01755123456",
        },
    )
    assert pay_res.status_code == 200
    assert pay_res.json()["gateway"] == "bKash-Payment-Gateway"
    assert pay_res.json()["amount_paid"] == 1050.0

    # Step 10: Prescribe and complete consultation
    rx_res = client.post(
        "/api/records/prescribe",
        json={
            "appointment_id": appt_id,
            "diagnosis": "Asthenopia (Computer Vision Syndrome)",
            "notes": "Follow 20-20-20 rule. Prescribed lubricating artificial tears.",
            "prescriptions": [
                {
                    "medicine_name": "Carboxymethylcellulose 0.5% Eye Drops",
                    "dosage": "1 drop",
                    "frequency": "4 times daily in both eyes",
                    "duration_days": 30,
                }
            ],
        },
    )
    assert rx_res.status_code == 201
    assert rx_res.json()["record"]["diagnosis"] == "Asthenopia (Computer Vision Syndrome)"

