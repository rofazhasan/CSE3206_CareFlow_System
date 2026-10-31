import pytest
import tempfile
from careflow.models.appointment import Appointment, AppointmentStatus
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


# ==========================================
# Factory Method Pattern Tests
# ==========================================

def test_notification_factory_instantiates_correct_channels():
    email_channel = NotificationFactory.create_channel("email", smtp_host="smtp.ruet.ac.bd")
    sms_channel = NotificationFactory.create_channel("sms")
    webhook_channel = NotificationFactory.create_channel("webhook")

    assert isinstance(email_channel, EmailNotificationChannel)
    assert isinstance(sms_channel, SMSNotificationChannel)
    assert isinstance(webhook_channel, WebhookNotificationChannel)

    res_email = email_channel.send("doctor@ruet.ac.bd", "Schedule Alert", "You have 3 appointments today.")
    assert res_email["status"] == "SENT"
    assert res_email["channel"] == "EMAIL"
    assert res_email["gateway"] == "smtp.ruet.ac.bd"

    res_sms = sms_channel.send("+8801712345678", "Slot Booked", "Confirmed at 10 AM.")
    assert res_sms["status"] == "SENT"
    assert "Confirmed at 10 AM" in res_sms["body"]


def test_notification_factory_unsupported_channel_raises_error():
    with pytest.raises(ValueError, match="Unsupported notification channel"):
        NotificationFactory.create_channel("carrier_pigeon")


def test_notification_factory_dynamic_registration():
    class SlackChannel(INotificationChannel):
        def send(self, recipient: str, subject: str, message: str) -> dict:
            return {"status": "SENT", "channel": "SLACK", "recipient": recipient}

    NotificationFactory.register_channel("slack", SlackChannel)
    slack = NotificationFactory.create_channel("slack")
    assert isinstance(slack, SlackChannel)
    assert slack.send("#alerts", "Alert", "Test")["channel"] == "SLACK"


# ==========================================
# Adapter Pattern Tests
# ==========================================

def test_bkash_payment_adapter_success():
    adapter = BkashPaymentAdapter()
    result = adapter.process_payment(
        amount=1500.0,
        reference_id="INV-001",
        customer_info={"phone": "01711223344"},
    )
    assert result.success is True
    assert result.amount_paid == 1500.0
    assert result.currency == "BDT"
    assert result.transaction_id.startswith("BKASH-")
    assert result.gateway_name == "bKash-Payment-Gateway"


def test_bkash_payment_adapter_invalid_phone_fails():
    adapter = BkashPaymentAdapter()
    result = adapter.process_payment(
        amount=1500.0,
        reference_id="INV-002",
        customer_info={"phone": "99999"},  # Invalid BD phone
    )
    assert result.success is False
    assert "Invalid Bangladesh mobile number" in result.error_message


def test_stripe_payment_adapter_success_and_cents_conversion():
    adapter = StripePaymentAdapter()
    result = adapter.process_payment(
        amount=50.25,
        reference_id="INV-003",
        customer_info={"email": "patient@ruet.ac.bd"},
    )
    assert result.success is True
    assert result.amount_paid == 50.25
    assert result.currency == "USD"
    assert result.transaction_id.startswith("ch_stripe_")


def test_stripe_payment_adapter_negative_amount_fails():
    adapter = StripePaymentAdapter()
    result = adapter.process_payment(
        amount=-10.0,
        reference_id="INV-004",
        customer_info={"email": "patient@ruet.ac.bd"},
    )
    assert result.success is False
    assert result.error_message == "amount_too_small"


# ==========================================
# Observer Pattern Tests
# ==========================================

def test_observer_pattern_notification_and_audit():
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

        appt = Appointment(
            patient_id="pat-100",
            doctor_id="doc-200",
            scheduled_time="2026-11-02T14:30:00",
            reason="Cardiology Evaluation",
        )
        appt.confirm()

        subject.notify(
            event_type="CONFIRMED",
            appointment=appt,
            metadata={"patient_email": "patient100@gmail.com", "patient_phone": "01700112233"},
        )

        # Check Email Observer
        assert len(email_obs.sent_emails) == 1
        assert "CONFIRMED" in email_obs.sent_emails[0]["message"]
        assert email_obs.sent_emails[0]["recipient"] == "patient100@gmail.com"

        # Check SMS Observer
        assert len(sms_obs.sent_sms) == 1
        assert "CONFIRMED" in sms_obs.sent_sms[0]["body"]

        # Check Audit Log in SQLite
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE entity_id = ?", (appt.appointment_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0]["event_type"] == "APPOINTMENT_CONFIRMED"

        # Test Detach
        subject.detach(sms_obs)
        appt.cancel()
        subject.notify("CANCELLED", appt, {})
        assert len(sms_obs.sent_sms) == 1  # No new SMS received after detachment
        assert len(email_obs.sent_emails) == 2  # Email still attached

        db.close()
        DatabaseManager.reset_instance()


# ==========================================
# Strategy Pattern Tests
# ==========================================

def test_billing_strategies():
    base_fee = 1000.0

    # Standard: 0 discount, 5% tax = 1050
    std = StandardBillingStrategy().compute(base_fee)
    assert std.discount_amount == 0.0
    assert std.tax_amount == 50.0
    assert std.final_payable == 1050.0

    # Student: 30% discount, 0 tax = 700
    student = StudentDiscountStrategy().compute(base_fee)
    assert student.discount_amount == 300.0
    assert student.tax_amount == 0.0
    assert student.final_payable == 700.0

    # Insurance: 80% discount, 0 tax = 200
    ins = InsuranceCoverageStrategy().compute(base_fee)
    assert ins.discount_amount == 800.0
    assert ins.tax_amount == 0.0
    assert ins.final_payable == 200.0

    # Emergency: 25% surcharge (1250) + 5% tax (62.50) = 1312.50
    emerg = EmergencyCareStrategy().compute(base_fee)
    assert emerg.final_payable == 1312.50
    assert "Emergency Triage Scheme" in emerg.scheme_name
