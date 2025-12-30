"""Notification handlers for SMS and email alerts."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Exception raised for notification errors."""
    pass


class SMSNotifier:
    """SMS notification handler using Twilio."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        """Initialize SMS notifier.

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: Twilio phone number
            to_number: Recipient phone number
        """
        self.from_number = from_number
        self.to_number = to_number
        self.enabled = bool(account_sid and auth_token and from_number and to_number)

        if self.enabled:
            try:
                self.client = Client(account_sid, auth_token)
                logger.info("SMS notifier initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
        else:
            logger.warning("SMS notifier disabled - missing credentials")

    def send(self, message: str) -> bool:
        """Send SMS message.

        Args:
            message: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("SMS notifier is disabled")
            return False

        try:
            msg = self.client.messages.create(
                to=self.to_number,
                from_=self.from_number,
                body=message
            )
            logger.info(f"SMS sent successfully: {msg.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return False


class EmailNotifier:
    """Email notification handler."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        email_address: str,
        email_password: str,
        recipient_email: str
    ):
        """Initialize email notifier.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            email_address: Sender email address
            email_password: Sender email password
            recipient_email: Recipient email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password
        self.recipient_email = recipient_email
        self.enabled = bool(
            smtp_server and email_address and email_password and recipient_email
        )

        if self.enabled:
            logger.info("Email notifier initialized successfully")
        else:
            logger.warning("Email notifier disabled - missing credentials")

    def send(self, subject: str, message: str, html: bool = False) -> bool:
        """Send email message.

        Args:
            subject: Email subject
            message: Email message (plain text or HTML)
            html: Whether the message is HTML

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email notifier is disabled")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email

            if html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {self.recipient_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False


class Notifier:
    """Unified notification handler."""

    def __init__(
        self,
        sms_notifier: Optional[SMSNotifier] = None,
        email_notifier: Optional[EmailNotifier] = None,
        sms_enabled: bool = True,
        email_enabled: bool = True
    ):
        """Initialize notifier.

        Args:
            sms_notifier: SMS notifier instance
            email_notifier: Email notifier instance
            sms_enabled: Whether SMS notifications are enabled
            email_enabled: Whether email notifications are enabled
        """
        self.sms_notifier = sms_notifier
        self.email_notifier = email_notifier
        self.sms_enabled = sms_enabled and sms_notifier and sms_notifier.enabled
        self.email_enabled = email_enabled and email_notifier and email_notifier.enabled

    def send_sms(self, message: str) -> bool:
        """Send SMS notification.

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        if not self.sms_enabled:
            return False
        return self.sms_notifier.send(message)

    def send_email(self, subject: str, message: str, html: bool = False) -> bool:
        """Send email notification.

        Args:
            subject: Email subject
            message: Email message
            html: Whether message is HTML

        Returns:
            True if sent successfully
        """
        if not self.email_enabled:
            return False
        return self.email_notifier.send(subject, message, html)

    def notify(self, message: str, subject: str = "Stock Price Alert") -> None:
        """Send notification via all enabled channels.

        Args:
            message: Message to send
            subject: Email subject (for email notifications)
        """
        sent_count = 0

        if self.sms_enabled:
            if self.send_sms(message):
                sent_count += 1

        if self.email_enabled:
            if self.send_email(subject, message):
                sent_count += 1

        if sent_count == 0:
            logger.warning("No notifications were sent (all channels disabled or failed)")
        else:
            logger.info(f"Notification sent via {sent_count} channel(s)")
