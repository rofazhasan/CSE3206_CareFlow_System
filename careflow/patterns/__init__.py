from .singleton import DatabaseManager
from .factory import (
    INotificationChannel,
    EmailNotificationChannel,
    SMSNotificationChannel,
    WebhookNotificationChannel,
    NotificationFactory,
)
from .adapter import (
    IPaymentProcessor,
    BkashGateway,
    StripeGateway,
    BkashPaymentAdapter,
    StripePaymentAdapter,
    PaymentResult,
)
from .observer import (
    IAppointmentObserver,
    AppointmentSubject,
    EmailNotificationObserver,
    SMSNotificationObserver,
    AuditLogObserver,
)
from .strategy import (
    IBillingStrategy,
    StandardBillingStrategy,
    StudentDiscountStrategy,
    InsuranceCoverageStrategy,
    EmergencyCareStrategy,
    BillingCalculationResult,
)

__all__ = [
    "DatabaseManager",
    "INotificationChannel",
    "EmailNotificationChannel",
    "SMSNotificationChannel",
    "WebhookNotificationChannel",
    "NotificationFactory",
    "IPaymentProcessor",
    "BkashGateway",
    "StripeGateway",
    "BkashPaymentAdapter",
    "StripePaymentAdapter",
    "PaymentResult",
    "IAppointmentObserver",
    "AppointmentSubject",
    "EmailNotificationObserver",
    "SMSNotificationObserver",
    "AuditLogObserver",
    "IBillingStrategy",
    "StandardBillingStrategy",
    "StudentDiscountStrategy",
    "InsuranceCoverageStrategy",
    "EmergencyCareStrategy",
    "BillingCalculationResult",
]

