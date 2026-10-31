from careflow.models.invoice import Invoice
from careflow.repositories.billing_repository import BillingRepository
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.patterns.strategy import StandardBillingStrategy
from careflow.patterns.adapter import BkashPaymentAdapter, PaymentResult


class BillingService:
    def __init__(self, billing_repo=None, appointment_repo=None, payment_processor=None):
        self.billing_repo = billing_repo or BillingRepository()
        self.appointment_repo = appointment_repo or AppointmentRepository()
        self.payment_processor = payment_processor or BkashPaymentAdapter()

    def generate_invoice(self, appointment_id: str, strategy=None, promo_discount: float = 0.0, notes: str = "") -> Invoice:
        """
        Generate invoice with base fee threshold check, Strategy discount calculation,
        and optional promo discount voucher.
        """
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment '{appointment_id}' does not exist.")
        if appt.fee < 100.0:
            raise ValueError("Base consultation fee cannot be below clinic minimum 100 BDT.")

        existing = self.billing_repo.get_by_appointment_id(appointment_id)
        if existing:
            return existing

        calc_strategy = strategy or StandardBillingStrategy()
        calc = calc_strategy.compute(appt.fee)
        total_discount = min(appt.fee, calc.discount_amount + promo_discount)

        invoice = Invoice(
            appointment_id=appointment_id,
            patient_id=appt.patient_id,
            base_amount=calc.base_amount,
            discount_amount=total_discount,
            tax_amount=calc.tax_amount,
            status="UNPAID",
        )
        return self.billing_repo.create_invoice(invoice)

    def process_invoice_payment(self, invoice_id: str, customer_info: dict, custom_processor=None) -> PaymentResult:
        invoice = self.billing_repo.get_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice '{invoice_id}' does not exist.")
        if invoice.status == "PAID":
            raise ValueError(f"Invoice '{invoice_id}' is already settled.")

        processor = custom_processor or self.payment_processor
        result = processor.process_payment(
            amount=invoice.total_payable,
            reference_id=invoice.invoice_id,
            customer_info=customer_info,
        )

        if result.success:
            self.billing_repo.update_payment(invoice.invoice_id, "PAID", result.transaction_id)
            invoice.mark_as_paid(result.transaction_id)

        return result

    def get_invoice(self, invoice_id: str):
        return self.billing_repo.get_by_id(invoice_id)
