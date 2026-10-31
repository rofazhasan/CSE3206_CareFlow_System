"""
CareFlow CLI Interactive Simulator.
RUET CSE 3206 Software Engineering Sessional.
"""

from careflow.patterns.singleton import DatabaseManager
from careflow.patterns.strategy import StudentDiscountStrategy
from careflow.patterns.adapter import BkashPaymentAdapter
from careflow.patterns.observer import (
    AppointmentSubject,
    EmailNotificationObserver,
    SMSNotificationObserver,
    AuditLogObserver,
)
from careflow.repositories.user_repository import UserRepository
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.repositories.billing_repository import BillingRepository
from careflow.repositories.medical_record_repository import MedicalRecordRepository
from careflow.services.auth_service import AuthService
from careflow.services.appointment_service import AppointmentService
from careflow.services.billing_service import BillingService
from careflow.services.medical_record_service import MedicalRecordService
from careflow.models.medical_record import PrescriptionItem


def run_demo():
    print("=" * 65)
    print("  CAREFLOW: SMART CLINIC APPOINTMENT & BILLING SYSTEM")
    print("  RUET CSE 3206 Software Engineering Sessional Demo")
    print("=" * 65)

    db = DatabaseManager("careflow_demo.db")
    user_repo = UserRepository(db)
    appt_repo = AppointmentRepository(db)
    bill_repo = BillingRepository(db)
    rec_repo = MedicalRecordRepository(db)

    subject = AppointmentSubject()
    email_obs = EmailNotificationObserver()
    sms_obs = SMSNotificationObserver()
    audit_obs = AuditLogObserver(db)
    subject.attach(email_obs)
    subject.attach(sms_obs)
    subject.attach(audit_obs)

    auth_service = AuthService(user_repo)
    appt_service = AppointmentService(appt_repo, user_repo, subject)
    billing_service = BillingService(bill_repo, appt_repo, BkashPaymentAdapter())
    record_service = MedicalRecordService(rec_repo, appt_repo)

    print("\n[Step 1] Registering Doctor and Patient...")
    doctor = user_repo.get_by_email("doctor@ruet.ac.bd") or auth_service.register_user(
        "Dr. Md. Ali", "doctor@ruet.ac.bd", "Pass1234", "DOCTOR", "01711223344"
    )
    patient = user_repo.get_by_email("student@ruet.ac.bd") or auth_service.register_user(
        "Md. Rofaz Hasan Rafiu", "student@ruet.ac.bd", "Pass1234", "PATIENT", "01811223344"
    )
    print(f"  ✓ Doctor: {doctor.name} ({doctor.role})")
    print(f"  ✓ Patient: {patient.name} ({patient.role})")

    print("\n[Step 2] Booking Appointment & Notifying Observers...")
    slot = "2026-11-20 10:00 AM"
    appt = appt_service.book_appointment(
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        scheduled_time=slot,
        reason="Fever and persistent headache",
        fee=1200.0,
    )
    print(f"  ✓ Appointment ID: {appt.appointment_id} | Status: {appt.status}")
    print(f"  ✓ Observer Alert: Email delivered to {email_obs.sent_emails[-1]['recipient']}")
    print(f"  ✓ Observer Alert: SMS delivered to {sms_obs.sent_sms[-1]['phone']}")

    print("\n[Step 3] Doctor Confirms Appointment...")
    confirmed = appt_service.confirm_appointment(appt.appointment_id)
    print(f"  ✓ Status Updated: {confirmed.status}")

    print("\n[Step 4] Strategy Pattern: Applying RUET Student Subsidy (30%)...")
    strategy = StudentDiscountStrategy()
    invoice = billing_service.generate_invoice(appt.appointment_id, strategy=strategy)
    print(f"  ✓ Scheme: {strategy.compute(appt.fee).scheme_name}")
    print(f"  ✓ Base Consultation Fee: {invoice.base_amount:.2f} BDT")
    print(f"  ✓ Student Discount (30%): -{invoice.discount_amount:.2f} BDT")
    print(f"  ✓ Final Amount Payable: {invoice.total_payable:.2f} BDT")

    print("\n[Step 5] Adapter Pattern: Paying via bKash Payment Adapter...")
    pay_res = billing_service.process_invoice_payment(
        invoice_id=invoice.invoice_id,
        customer_info={"phone": patient.phone},
    )
    print(f"  ✓ Payment Status: SUCCESS via {pay_res.gateway_name}")
    print(f"  ✓ Transaction ID: {pay_res.transaction_id}")

    print("\n[Step 6] Issuing Electronic Prescription...")
    med = PrescriptionItem("Paracetamol", "500mg", "1-0-1 after food", 5)
    rec = record_service.create_record(
        appointment_id=appt.appointment_id,
        diagnosis="Viral Fever",
        notes="Adequate bed rest and oral hydration.",
        prescriptions=[med],
    )
    print(f"  ✓ Diagnosis: {rec.diagnosis}")
    print(f"  ✓ Medication: {med.medicine_name} ({med.dosage})")
    print(f"  ✓ Final Status: {appt_repo.get_by_id(appt.appointment_id).status}")

    print("\n" + "=" * 65)
    print("  DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_demo()
