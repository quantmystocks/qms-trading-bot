"""Email notification module."""

from .email_notifier import EmailNotifier
from .email_factory import create_email_notifier

__all__ = ["EmailNotifier", "create_email_notifier"]
