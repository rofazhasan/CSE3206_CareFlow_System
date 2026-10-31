from typing import Optional, Dict, Any
from careflow.models.invoice import Invoice, PaymentStatus
from careflow.repositories.billing_repository import BillingRepository
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.patterns.strategy import IBillingStrategy, StandardBillingStrategy
from careflow.patterns.adapter import IPaymentProcessor, BkashPaymentAdapter, PaymentResult


class BillingService:
    """
    Billing Service orchestrating invoice creation and payment settlement.
    Applies the Strategy Pattern for flexible discount/tax computation
    and the Adapter Pattern for polymorphic gateway execution.
    """

    def __init__(
        self,
        billing_repo: Optional[BillingRepository] = None,
        appointment_repo: Optional[AppointmentRepository] = None,
        payment_processor: Optional[IPaymentProcessor] = None,
    ):
        self.billing_repo = billing_repo or BillingRepository()
        self.appointment_repo = appointment_repo or AppointmentRepository()
        self.payment_processor = payment_processor or BkashPaymentAdapter()

    def generate_invoice(
        self,
        appointment_id: str,
        strategy: Optional[IBillingStrategy] = None,
        promo_discount: float = 0.0,
    ) -> Invoice:
        """Generate invoice with optional promotional discount voucher."""
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment '{appointment_id}' does not exist.")

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
            status=PaymentStatus.UNPAID,
        )
        return self.billing_repo.create_invoice(invoice)

    def process_invoice_payment(
        self,
        invoice_id: str,
        customer_info: Dict[str, Any],
        custom_processor: Optional[IPaymentProcessor] = None,
    ) -> PaymentResult:
        invoice = self.billing_repo.get_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice '{invoice_id}' does not exist.")

        if invoice.status == PaymentStatus.PAID:
            raise ValueError(f"Invoice '{invoice_id}' is already settled.")

        processor = custom_processor or self.payment_processor
        result = processor.process_payment(
            amount=invoice.total_payable,
            reference_id=invoice.invoice_id,
            customer_info=customer_info,
        )

        if result.success:
            self.billing_repo.update_payment(
                invoice_id=invoice.invoice_id,
                status=PaymentStatus.PAID,
                reference=result.transaction_id,
            )
            invoice.mark_as_paid(result.transaction_id)

        return result

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        return self.billing_repo.get_by_id(invoice_id)
