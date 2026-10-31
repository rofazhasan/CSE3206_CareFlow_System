"""
Adapter Pattern (Structural Category).
Converts incompatible interfaces of third-party payment gateways (bKash, Stripe)
into a unified IPaymentProcessor interface required by CareFlow billing.

Problem Solved:
  Real-world payment APIs differ fundamentally:
  - bKash uses BDT floating currency, an MSISDN phone string, and custom execute APIs.
  - Stripe uses integer amounts in cents, currency ISO codes, and idempotency headers.
  Without an adapter, the clinic billing module would become riddled with vendor-specific
  logic, tight coupling, and breaking changes whenever a gateway updates.

Alternative Rejected:
  Direct Vendor Integration with if/else branches:
  - Strongly couples billing service to third-party SDK signatures.
  - Swapping or upgrading payment providers requires changing core invoice code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    amount_paid: float
    currency: str
    gateway_name: str
    error_message: Optional[str] = None


class IPaymentProcessor(ABC):
    """Target interface expected by CareFlow Billing Service."""

    @abstractmethod
    def process_payment(self, amount: float, reference_id: str, customer_info: dict) -> PaymentResult:
        """Process transaction and return normalized PaymentResult."""
        pass


# ==========================================
# Incompatible Adaptees (Third-Party SDKs)
# ==========================================

class BkashGateway:
    """Adaptee 1: Represents third-party bKash Merchant API."""

    def __init__(self, merchant_wallet: str = "01700000000"):
        self.merchant_wallet = merchant_wallet

    def execute_bKash_payment(self, msisdn: str, bdt_amount: float, merchant_token: str) -> dict:
        """Vendor-specific method signature."""
        if not msisdn.startswith("01") or len(msisdn) != 11:
            return {"status": "FAILED", "err_code": "INVALID_MSISDN", "message": "Invalid Bangladesh mobile number"}
        if bdt_amount <= 0:
            return {"status": "FAILED", "err_code": "INVALID_AMOUNT", "message": "Amount must be positive"}
        
        trx_id = f"BKASH-{uuid.uuid4().hex[:10].upper()}"
        return {
            "status": "COMPLETED",
            "trxID": trx_id,
            "amount": bdt_amount,
            "currency": "BDT",
            "customerMsisdn": msisdn,
            "token": merchant_token,
        }


class StripeGateway:
    """Adaptee 2: Represents third-party Stripe Payments API."""

    def __init__(self, api_key: str = "sk_test_ruet_clinic"):
        self.api_key = api_key

    def charge_customer_cents(self, amount_in_cents: int, currency: str, customer_email: str, idempotency_key: str) -> dict:
        """Vendor-specific method signature requiring cents and idempotency."""
        if amount_in_cents <= 0:
            return {"paid": False, "failure_code": "amount_too_small"}
        
        charge_id = f"ch_stripe_{uuid.uuid4().hex[:12]}"
        return {
            "paid": True,
            "id": charge_id,
            "amount": amount_in_cents,
            "currency": currency.lower(),
            "receipt_email": customer_email,
            "idempotency_key": idempotency_key,
        }


# ==========================================
# Concrete Adapters
# ==========================================

class BkashPaymentAdapter(IPaymentProcessor):
    """Adapts BkashGateway to IPaymentProcessor."""

    def __init__(self, bkash_gateway: Optional[BkashGateway] = None, app_token: str = "RUET-TOKEN-2026"):
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
                currency=response["currency"],
                gateway_name="bKash-Payment-Gateway",
            )
        else:
            return PaymentResult(
                success=False,
                transaction_id="",
                amount_paid=0.0,
                currency="BDT",
                gateway_name="bKash-Payment-Gateway",
                error_message=response.get("message", "bKash transaction rejected"),
            )


class StripePaymentAdapter(IPaymentProcessor):
    """Adapts StripeGateway to IPaymentProcessor."""

    def __init__(self, stripe_gateway: Optional[StripeGateway] = None):
        self.gateway = stripe_gateway or StripeGateway()

    def process_payment(self, amount: float, reference_id: str, customer_info: dict) -> PaymentResult:
        # Convert standard float currency into integer cents
        amount_cents = int(round(amount * 100))
        email = customer_info.get("email", "patient@clinic.org")
        
        response = self.gateway.charge_customer_cents(
            amount_in_cents=amount_cents,
            currency="usd",
            customer_email=email,
            idempotency_key=f"idem_{reference_id}",
        )

        if response.get("paid") is True:
            return PaymentResult(
                success=True,
                transaction_id=response["id"],
                amount_paid=amount,
                currency="USD",
                gateway_name="Stripe-Gateway",
            )
        else:
            return PaymentResult(
                success=False,
                transaction_id="",
                amount_paid=0.0,
                currency="USD",
                gateway_name="Stripe-Gateway",
                error_message=response.get("failure_code", "Stripe payment failed"),
            )
