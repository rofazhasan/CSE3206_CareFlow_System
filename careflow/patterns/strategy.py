"""
Strategy Pattern (Behavioral Category).
Encapsulates interchangeable pricing and subsidy calculation algorithms.
"""

from abc import ABC, abstractmethod


class BillingCalculationResult:
    def __init__(self, base_amount: float, discount_amount: float, tax_amount: float, final_payable: float, scheme_name: str):
        self.base_amount = float(base_amount)
        self.discount_amount = float(discount_amount)
        self.tax_amount = float(tax_amount)
        self.final_payable = float(final_payable)
        self.scheme_name = scheme_name


class IBillingStrategy(ABC):
    @abstractmethod
    def compute(self, base_amount: float) -> BillingCalculationResult:
        pass


class StandardBillingStrategy(IBillingStrategy):
    """Standard consultation: 0% discount, 5% healthcare service tax."""
    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = 0.0
        tax = round(base_amount * 0.05, 2)
        total = round(base_amount - discount + tax, 2)
        return BillingCalculationResult(base_amount, discount, tax, total, "Standard Outpatient Scheme")


class StudentDiscountStrategy(IBillingStrategy):
    """University student subsidy (RUET scheme): 30% discount, 0% tax."""
    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = round(base_amount * 0.30, 2)
        tax = 0.0
        total = round(base_amount - discount + tax, 2)
        return BillingCalculationResult(base_amount, discount, tax, total, "University Student Subsidy (30%)")


class InsuranceCoverageStrategy(IBillingStrategy):
    """Corporate insurance: 80% coverage, 0% tax."""
    def compute(self, base_amount: float) -> BillingCalculationResult:
        discount = round(base_amount * 0.80, 2)
        tax = 0.0
        total = round(base_amount - discount + tax, 2)
        return BillingCalculationResult(base_amount, discount, tax, total, "Corporate Insurance (80%)")


class EmergencyCareStrategy(IBillingStrategy):
    """Emergency department care: 25% urgent staffing surcharge + 5% tax."""
    def compute(self, base_amount: float) -> BillingCalculationResult:
        surcharge = round(base_amount * 0.25, 2)
        tax = round((base_amount + surcharge) * 0.05, 2)
        total = round(base_amount + surcharge + tax, 2)
        return BillingCalculationResult(base_amount, 0.0, surcharge + tax, total, "Emergency Triage Scheme")
