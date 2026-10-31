import pytest
import tempfile
from careflow.models.appointment import Appointment
from careflow.patterns.singleton import DatabaseManager
from careflow.patterns.factory import (
    NotificationFactory,
    EmailNotificationChannel,
    SMSNotificationChannel,
    WebhookNotificationChannel,
    INotificationChannel,
)
from careflow.patterns.adapter import (
    BkashGateway,
    StripeGateway,
    BkashPaymentAdapter,
    StripePaymentAdapter,
)
from careflow.patterns.observer import (
    AppointmentSubject,
    EmailNotificationObserver,
    SMSNotificationObserver,
    AuditLogObserver,
)
from careflow.patterns.strategy import (
    StandardBillingStrategy,
    StudentDiscountStrategy,
    InsuranceCoverageStrategy,
    EmergencyCareStrategy,
)


def test_notification_factory():
    email = NotificationFactory.create_channel("email")
    sms = NotificationFactory.create_channel("sms")
    webhook = NotificationFactory.create_channel("webhook")

    assert isinstance(email, EmailNotificationChannel)
    assert isinstance(sms, SMSNotificationChannel)
    assert isinstance(webhook, WebhookNotificationChannel)

    res = email.send("test@ruet.ac.bd", "Hello", "Your appointment is set.")
    assert res["status"] == "SENT"
    assert res["channel"] == "EMAIL"

    with pytest.raises(ValueError):
        NotificationFactory.create_channel("unknown_channel")


def test_payment_adapters():
    # bKash Adapter
    bkash_adapter = BkashPaymentAdapter()
    res1 = bkash_adapter.process_payment(1200.0, "INV-1", {"phone": "01711223344"})
    assert res1.success is True
    assert res1.currency == "BDT"
    assert res1.transaction_id.startswith("BKASH-")

    # Invalid phone fails
    res_bad = bkash_adapter.process_payment(1200.0, "INV-2", {"phone": "123"})
    assert res_bad.success is False

    # Stripe Adapter
    stripe_adapter = StripePaymentAdapter()
    res2 = stripe_adapter.process_payment(50.0, "INV-3", {"email": "patient@ruet.ac.bd"})
    assert res2.success is True
    assert res2.currency == "USD"
    assert res2.transaction_id.startswith("ch_stripe_")

    # Invalid amount fails
    res_bad_stripe = stripe_adapter.process_payment(-10.0, "INV-4", {})
    assert res_bad_stripe.success is False


def test_observer_pattern():
    DatabaseManager.reset_instance()
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db = DatabaseManager(tmp.name)
        subject = AppointmentSubject()

        email_obs = EmailNotificationObserver()
        sms_obs = SMSNotificationObserver()
        audit_obs = AuditLogObserver(db)

        subject.attach(email_obs)
        subject.attach(sms_obs)
        subject.attach(audit_obs)

        appt = Appointment("p1", "d1", "2026-11-20 10:00", "Fever")
        appt.confirm()

        subject.notify("CONFIRMED", appt, {"patient_email": "patient@ruet.ac.bd", "patient_phone": "01711223344"})

        assert len(email_obs.sent_emails) == 1
        assert len(sms_obs.sent_sms) == 1

        # Check SQLite audit log
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE entity_id = ?", (appt.appointment_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1

        # Test detach
        subject.detach(sms_obs)
        appt.cancel()
        subject.notify("CANCELLED", appt, {})
        assert len(sms_obs.sent_sms) == 1  # Unchanged
        assert len(email_obs.sent_emails) == 2  # Received

        db.close()
        DatabaseManager.reset_instance()


def test_strategy_pattern():
    base_fee = 1000.0

    # Standard: 5% tax = 1050
    std = StandardBillingStrategy().compute(base_fee)
    assert std.discount_amount == 0.0
    assert std.tax_amount == 50.0
    assert std.final_payable == 1050.0

    # Student: 30% discount = 700
    student = StudentDiscountStrategy().compute(base_fee)
    assert student.discount_amount == 300.0
    assert student.tax_amount == 0.0
    assert student.final_payable == 700.0

    # Insurance: 80% discount = 200
    ins = InsuranceCoverageStrategy().compute(base_fee)
    assert ins.discount_amount == 800.0
    assert ins.final_payable == 200.0

    # Emergency: 25% surcharge + 5% tax
    emerg = EmergencyCareStrategy().compute(base_fee)
    assert emerg.final_payable == 1312.50
