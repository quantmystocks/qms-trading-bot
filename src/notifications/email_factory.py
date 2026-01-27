"""Factory for creating email notifier instances."""

import logging
from typing import Optional

from ..config import get_config
from .email_notifier import EmailNotifier
from .smtp_notifier import SMTPNotifier
from .sendgrid_notifier import SendGridNotifier
from .ses_notifier import SESNotifier

logger = logging.getLogger(__name__)


def create_email_notifier() -> Optional[EmailNotifier]:
    """
    Create an email notifier instance based on configuration.
    
    Returns:
        EmailNotifier instance or None if email is disabled
    """
    config = get_config()
    
    if not config.email.enabled:
        logger.info("Email notifications are disabled")
        return None
    
    if not config.email.recipient:
        logger.warning("Email is enabled but no recipient specified")
        return None
    
    provider = config.email.provider
    
    try:
        if provider == "smtp":
            if not all([
                config.email.smtp_host,
                config.email.smtp_username,
                config.email.smtp_password,
                config.email.smtp_from_email,
            ]):
                logger.error("SMTP credentials are incomplete")
                return None
            
            return SMTPNotifier(
                smtp_host=config.email.smtp_host,
                smtp_port=config.email.smtp_port,
                smtp_username=config.email.smtp_username,
                smtp_password=config.email.smtp_password,
                from_email=config.email.smtp_from_email,
            )
        
        elif provider == "sendgrid":
            if not config.email.sendgrid_api_key or not config.email.sendgrid_from_email:
                logger.error("SendGrid credentials are incomplete")
                return None
            
            return SendGridNotifier(
                api_key=config.email.sendgrid_api_key,
                from_email=config.email.sendgrid_from_email,
            )
        
        elif provider == "ses":
            if not all([
                config.email.aws_region,
                config.email.aws_access_key_id,
                config.email.aws_secret_access_key,
                config.email.ses_from_email,
            ]):
                logger.error("AWS SES credentials are incomplete")
                return None
            
            return SESNotifier(
                region=config.email.aws_region,
                access_key_id=config.email.aws_access_key_id,
                secret_access_key=config.email.aws_secret_access_key,
                from_email=config.email.ses_from_email,
            )
        
        else:
            logger.error(f"Unsupported email provider: {provider}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating email notifier: {e}")
        return None
