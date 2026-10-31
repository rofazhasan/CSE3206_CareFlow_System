"""
Factory Method Pattern (Creational Category).
Creates the appropriate notification channel object (Email, SMS, Webhook)
without exposing creation logic directly to the caller.
"""

from abc import ABC, abstractmethod


class INotificationChannel(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str) -> dict:
        pass


class EmailNotificationChannel(INotificationChannel):
    def __init__(self, smtp_host="smtp.careflow.com"):
        self.smtp_host = smtp_host

    def send(self, recipient: str, subject: str, message: str) -> dict:
        return {
            "status": "SENT",
            "channel": "EMAIL",
            "recipient": recipient,
            "subject": subject,
            "message": message,
        }


class SMSNotificationChannel(INotificationChannel):
    def __init__(self, sender_id="CareFlow"):
        self.sender_id = sender_id

    def send(self, recipient: str, subject: str, message: str) -> dict:
        return {
            "status": "SENT",
            "channel": "SMS",
            "recipient": recipient,
            "message": f"[{subject}] {message}",
        }


class WebhookNotificationChannel(INotificationChannel):
    def __init__(self, webhook_url="https://hooks.clinic.org"):
        self.webhook_url = webhook_url

    def send(self, recipient: str, subject: str, message: str) -> dict:
        return {
            "status": "SENT",
            "channel": "WEBHOOK",
            "recipient": recipient,
            "payload": {"title": subject, "body": message},
        }


class NotificationFactory:
    """
    Factory Method class that instantiates notification channels based on type.
    """
    _channels = {
        "email": EmailNotificationChannel,
        "sms": SMSNotificationChannel,
        "webhook": WebhookNotificationChannel,
    }

    @classmethod
    def create_channel(cls, channel_type: str, **kwargs) -> INotificationChannel:
        channel_key = channel_type.lower()
        if channel_key not in cls._channels:
            raise ValueError(f"Unsupported notification channel '{channel_type}'. Choose from: email, sms, webhook")
        return cls._channels[channel_key](**kwargs)

    @classmethod
    def register_channel(cls, channel_name: str, channel_class):
        cls._channels[channel_name.lower()] = channel_class
