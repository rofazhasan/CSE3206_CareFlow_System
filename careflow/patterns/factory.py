"""
Factory Method Pattern (Creational Category).
Decouples notification dispatch clients from concrete channel transport logic.

Problem Solved:
  Directly instantiating Email or SMS senders inside service layers causes tight coupling
  to third-party vendor APIs, makes unit testing difficult, and violates the Open-Closed Principle.

Alternative Rejected:
  Conditionals (if-elif-else) in business logic:
  - Whenever a new channel (e.g. WhatsApp, Slack, Webhook) is added, core business code
    must be reopened and modified, risking regressions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class INotificationChannel(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        """Dispatch notification to specified recipient."""
        pass


class EmailNotificationChannel(INotificationChannel):
    def __init__(self, smtp_host: str = "smtp.clinic.careflow.com"):
        self.smtp_host = smtp_host

    def send(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        # In production this connects to SMTP/SendGrid. For testing/demo, it returns dispatch payload.
        return {
            "status": "SENT",
            "channel": "EMAIL",
            "recipient": recipient,
            "subject": subject,
            "body": message,
            "gateway": self.smtp_host,
        }


class SMSNotificationChannel(INotificationChannel):
    def __init__(self, sms_api_key: str = "SMS-PROD-KEY-RUET"):
        self.sms_api_key = sms_api_key

    def send(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        # Formatted for cellular telco gateway
        return {
            "status": "SENT",
            "channel": "SMS",
            "recipient": recipient,
            "body": f"[{subject}] {message}",
            "gateway": "TelcoSMS-Aggregator",
        }


class WebhookNotificationChannel(INotificationChannel):
    def __init__(self, endpoint_url: str = "https://hooks.clinic.org/events"):
        self.endpoint_url = endpoint_url

    def send(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        return {
            "status": "SENT",
            "channel": "WEBHOOK",
            "recipient": recipient,
            "payload": {"title": subject, "content": message},
            "endpoint": self.endpoint_url,
        }


class NotificationFactory:
    """
    Factory Method class responsible for instantiating the appropriate
    notification channel handler based on channel type string.
    """
    _registry: Dict[str, type] = {
        "email": EmailNotificationChannel,
        "sms": SMSNotificationChannel,
        "webhook": WebhookNotificationChannel,
    }

    @classmethod
    def register_channel(cls, channel_type: str, channel_cls: type) -> None:
        """Extensibility hook allowing new channels to be registered at runtime."""
        cls._registry[channel_type.lower()] = channel_cls

    @classmethod
    def create_channel(cls, channel_type: str, **kwargs) -> INotificationChannel:
        """Factory Method to construct channel instance."""
        target_cls = cls._registry.get(channel_type.lower())
        if not target_cls:
            valid_channels = ", ".join(cls._registry.keys())
            raise ValueError(f"Unsupported notification channel '{channel_type}'. Supported: {valid_channels}")
        return target_cls(**kwargs)
