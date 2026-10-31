"""
CareFlow CLI Interactive Simulator.
RUET CSE 3206 Software Engineering Sessional.
Allows instant live demonstration of the complete clinic lifecycle in terminal.
"""

import sys
from careflow.models.user import UserRole
from careflow.patterns.singleton import DatabaseManager
from careflow.patterns.strategy import (
    StandardBillingStrategy,
    StudentDiscountStrategy,
    InsuranceCoverageStrategy,
    EmergencyCareStrategy,
)
from careflow.patterns.adapter import BkashPaymentAdapter, StripePaymentAdapter
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
    print("=" * 70)
    print("  CAREFLOW - SMART CLINIC APPOINTMENT & BILLING SYSTEM")
    print("  RUET CSE 3206 Software Engineering Sessional Live Demonstration")
    print("=" * 70)

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

    print("\n[Step 1] Registering System Users...")
    try:
        doctor = auth_service.register_user(
            name="Dr. Kazi Md. Rokibul Hasan",
            email="rokibul.doc@ruet.ac.bd",
            password="DocPassword2026",
            role=UserRole.DOCTOR,
            phone="01712001122",
        )
    except ValueError:
        doctor = user_repo.get_by_email("rokibul.doc@ruet.ac.bd")
    print(f"  ✓ Doctor Registered: {doctor.name} ({doctor.email}) [ID: {doctor.user_id[:8]}]")

    try:
        patient = auth_service.register_user(
            name="Md. Rofaz Hasan Rafiu",
            email="rofaz.student@ruet.ac.bd",
            password="StudentKey2026",
            role=UserRole.PATIENT,
            phone="01844556677",
        )
    except ValueError:
        patient = user_repo.get_by_email("rofaz.student@ruet.ac.bd")
    print(f"  ✓ Patient Registered: {patient.name} ({patient.email}) [ID: {patient.user_id[:8]}]")

    print("\n[Step 2] Booking Appointment & Triggering Observer Notifications...")
    slot = "2026-11-15T10:30:00"
    appt = appt_service.book_appointment(
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        scheduled_time=slot,
        reason="Persistent dry cough and mild respiratory distress",
        fee=1200.0,
    )
    print(f"  ✓ Appointment Created: ID {appt.appointment_id[:8]} | Status: {appt.status.value}")
    print(f"  ✓ Observer Event Sent: Email sent to {email_obs.sent_emails[-1]['recipient']}")
    print(f"  ✓ Observer Event Sent: SMS sent to {sms_obs.sent_sms[-1]['phone']}")

    print("\n[Step 3] Doctor Confirms Appointment...")
    confirmed = appt_service.confirm_appointment(appt.appointment_id)
    print(f"  ✓ Appointment Confirmed: Status -> {confirmed.status.value}")

    print("\n[Step 4] Applying Strategy Pattern for Billing Calculation...")
    # Demonstrating Student Discount Strategy (30% waiver)
    strategy = StudentDiscountStrategy()
    invoice = billing_service.generate_invoice(appt.appointment_id, strategy=strategy)
    print(f"  ✓ Scheme: University Student Medical Subsidy")
    print(f"  ✓ Base Fee: {invoice.base_amount:.2f} BDT")
    print(f"  ✓ 30% Subsidy Discount: -{invoice.discount_amount:.2f} BDT")
    print(f"  ✓ Total Payable: {invoice.total_payable:.2f} BDT | Status: {invoice.status.value}")

    print("\n[Step 5] Settle Payment via Structural Adapter Pattern (bKash)...")
    pay_result = billing_service.process_invoice_payment(
        invoice_id=invoice.invoice_id,
        customer_info={"phone": patient.phone},
    )
    print(f"  ✓ Payment Executed via Adapter: {pay_result.gateway_name}")
    print(f"  ✓ Transaction ID: {pay_result.transaction_id}")
    print(f"  ✓ Amount Settled: {pay_result.amount_paid:.2f} {pay_result.currency}")

    print("\n[Step 6] Issuing Electronic Prescription & Completing Consultation...")
    rx = PrescriptionItem("Montelukast", "10mg", "0-0-1 daily at bed time", 15)
    rec = record_service.create_record(
        appointment_id=appt.appointment_id,
        diagnosis="Mild Allergic Rhinitis with Bronchospasm",
        notes="Avoid sudden exposure to cold air and dust. Review after two weeks.",
        prescriptions=[rx],
    )
    print(f"  ✓ Clinical Diagnosis: {rec.diagnosis}")
    print(f"  ✓ Prescribed: {rx.medicine_name} ({rx.dosage}, {rx.frequency}, {rx.duration_days} days)")
    print(f"  ✓ Final Appointment Status: {appt_repo.get_by_id(appt.appointment_id).status.value}")

    print("\n" + "=" * 70)
    print("  ALL 5 MODULES & DESIGN PATTERNS EXECUTED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
