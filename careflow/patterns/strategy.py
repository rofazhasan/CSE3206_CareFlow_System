"""
Strategy Pattern (Behavioral Category).
Encapsulates interchangeable pricing and subsidy calculation algorithms.

Problem Solved:
  Clinic billing policies change frequently based on patient eligibility (e.g. general patients,
  university students, insured corporate patients, or emergency triage cases).
  Embedding these calculations inside Invoice or BillingService creates bulky, conditional
  spaghetti code with high cyclomatic complexity.

Alternative Rejected:
  Nested Switch/If Statements:
  - Adding a new subsidy scheme (e.g., Senior Citizen 40% discount) would require editing
    existing billing class conditionals, risking unintended regressions in standard billing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BillingCalculationResult:
    base_amount: float
    discount_amount: float
    tax_amount: float
    final_payable: float
    scheme_name: str
    breakdown_notes: str


class IBillingStrategy(ABC):
    @abstractmethod
    def compute(self, base_amount: float) -> BillingCalculationResult:
        """Calculate discount, tax, and final amount for a given base consultation fee."""
        pass


class StandardBillingStrategy(IBillingStrategy):
    """Standard outpatient consultation: 0% discount, 5% healthcare service tax."""

    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = 0.0
        tax = round(base_amount * 0.05, 2)
        total = round(base_amount - discount + tax, 2)
        return BillingCalculationResult(
            base_amount=base_amount,
            discount_amount=discount,
            tax_amount=tax,
            final_payable=total,
            scheme_name="Standard Outpatient Scheme",
            breakdown_notes="Standard fee with 5% statutory healthcare service tax.",
        )


class StudentDiscountStrategy(IBillingStrategy):
    """University student subsidy (RUET scheme): 30% medical waiver, 0% tax."""

    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = round(base_amount * 0.30, 2)
        tax = 0.0
        total = round(base_amount - discount + tax, 2)
        return BillingCalculationResult(
            base_amount=base_amount,
            discount_amount=discount,
            tax_amount=tax,
            final_payable=total,
            scheme_name="University Student Medical Subsidy",
            breakdown_notes="30% educational institution subsidy applied; tax exempt.",
        )


class InsuranceCoverageStrategy(IBillingStrategy):
    """Corporate health insurance: 80% coverage co-pay, 0% tax."""

    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = round(base_amount * 0.80, 2)
        tax = 0.0
        total = round(base_amount - discount + tax, 2)
        return BillingCalculationResult(
            base_amount=base_amount,
            discount_amount=discount,
            tax_amount=tax,
            final_payable=total,
            scheme_name="Corporate Health Insurance Scheme",
            breakdown_notes="80% primary claim settled via insurance; 20% patient co-pay.",
        )


class EmergencyCareStrategy(IBillingStrategy):
    """Emergency department care: 25% urgent staffing surcharge + 5% tax."""

    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = 0.0
        surcharge = round(base_amount * 0.25, 2)
        adjusted_base = base_amount + surcharge
        tax = round(adjusted_base * 0.05, 2)
        total = round(adjusted_base + tax, 2)
        return BillingCalculationResult(
            base_amount=base_amount,
            discount_amount=0.0,
            tax_amount=round(tax + surcharge, 2),  # reported under tax/surcharge bucket
            final_payable=total,
            scheme_name="Emergency Triage Scheme",
            breakdown_notes="Includes 25% emergency response surcharge and 5% service tax.",
        )
