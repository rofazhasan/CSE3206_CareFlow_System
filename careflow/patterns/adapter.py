"""
Adapter Pattern (Structural Category).
Adapts incompatible third-party payment gateways (bKash and Stripe)
to a unified IPaymentProcessor interface required by our clinic billing system.
"""

from abc import ABC, abstractmethod
import uuid


class PaymentResult:
    def __init__(self, success: bool, transaction_id: str, amount_paid: float, currency: str, gateway_name: str, error_message: str = None):
        self.success = success
        self.transaction_id = transaction_id
        self.amount_paid = float(amount_paid)
        self.currency = currency
        self.gateway_name = gateway_name
        self.error_message = error_message


class IPaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float, reference_id: str, customer_info: dict) -> PaymentResult:
        pass


# ==========================================
# Incompatible 3rd Party Adaptees
# ==========================================

class BkashGateway:
    """Simulates 3rd-party bKash merchant API with custom parameters."""
    def execute_bKash_payment(self, msisdn: str, bdt_amount: float, merchant_token: str) -> dict:
        if not msisdn.startswith("01") or len(msisdn) != 11:
            return {"status": "FAILED", "message": "Invalid Bangladesh mobile number"}
        if bdt_amount <= 0:
            return {"status": "FAILED", "message": "Amount must be positive"}
        
        trx_id = f"BKASH-{uuid.uuid4().hex[:8].upper()}"
        return {
            "status": "COMPLETED",
            "trxID": trx_id,
            "amount": bdt_amount,
            "currency": "BDT",
        }


class StripeGateway:
    """Simulates 3rd-party Stripe API requiring integer cents and currency."""
    def charge_customer_cents(self, amount_in_cents: int, currency: str, customer_email: str, idempotency_key: str) -> dict:
        if amount_in_cents <= 0:
            return {"paid": False, "failure_code": "amount_too_small"}
        
        charge_id = f"ch_stripe_{uuid.uuid4().hex[:8]}"
        return {
            "paid": True,
            "id": charge_id,
            "amount": amount_in_cents,
            "currency": currency,
        }


# ==========================================
# Concrete Adapters
# ==========================================

class BkashPaymentAdapter(IPaymentProcessor):
    def __init__(self, bkash_gateway=None, app_token="RUET-TOKEN-2026"):
        self.gateway = bkash_gateway or BkashGateway()
        self.app_token = app_token

    def process_payment(self, amount: float, reference_id: str, customer_info: dict) -> PaymentResult:
        phone = customer_info.get("phone", "01711223344")
        response = self.gateway.execute_bKash_payment(
            msisdn=phone,
            bdt_amount=amount,
            merchant_token=self.app_token,
        )
        if response.get("status") == "COMPLETED":
            return PaymentResult(
                success=True,
                transaction_id=response["trxID"],
                amount_paid=response["amount"],
                currency="BDT",
                gateway_name="bKash-Payment-Gateway",
            )
        return PaymentResult(
            success=False,
            transaction_id="",
            amount_paid=0.0,
            currency="BDT",
            gateway_name="bKash-Payment-Gateway",
            error_message=response.get("message", "bKash payment failed"),
        )


class StripePaymentAdapter(IPaymentProcessor):
    def __init__(self, stripe_gateway=None):
        self.gateway = stripe_gateway or StripeGateway()

    def process_payment(self, amount: float, reference_id: str, customer_info: dict) -> PaymentResult:
        cents = int(round(amount * 100))
        email = customer_info.get("email", "patient@clinic.org")
        response = self.gateway.charge_customer_cents(
            amount_in_cents=cents,
            currency="usd",
            customer_email=email,
            idempotency_key=f"idem_{reference_id}",
        )
        if response.get("paid"):
            return PaymentResult(
                success=True,
                transaction_id=response["id"],
                amount_paid=amount,
                currency="USD",
                gateway_name="Stripe-Gateway",
            )
        return PaymentResult(
            success=False,
            transaction_id="",
            amount_paid=0.0,
            currency="USD",
            gateway_name="Stripe-Gateway",
            error_message=response.get("failure_code", "Stripe payment failed"),
        )
