"""Configuration management for Stock Price Alerts."""

import os
import yaml
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration loader and manager."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration.

        Args:
            config_path: Path to the configuration YAML file
        """
        # Load environment variables
        load_dotenv()

        # Load YAML configuration
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Dictionary containing configuration
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_watchlist(self) -> List[str]:
        """Get the stock watchlist.

        Returns:
            List of stock symbols
        """
        return self.config.get('watchlist', [])

    def get_alert_schedule(self) -> List[Dict[str, str]]:
        """Get the alert schedule.

        Returns:
            List of scheduled alert configurations
        """
        return self.config.get('alert_schedule', [])

    def get_price_alerts_config(self) -> Dict[str, Any]:
        """Get price alert configuration.

        Returns:
            Price alerts configuration
        """
        return self.config.get('price_alerts', {})

    def get_notifications_config(self) -> Dict[str, Any]:
        """Get notifications configuration.

        Returns:
            Notifications configuration
        """
        return self.config.get('notifications', {})

    def get_market_hours(self) -> Dict[str, str]:
        """Get market hours configuration.

        Returns:
            Market hours configuration
        """
        return self.config.get('market_hours', {})

    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration.

        Returns:
            Storage configuration
        """
        return self.config.get('storage', {})

    def get_rate_limiting_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration.

        Returns:
            Rate limiting configuration
        """
        return self.config.get('rate_limiting', {})

    # Environment variables
    @property
    def alpha_vantage_api_key(self) -> str:
        """Get Alpha Vantage API key."""
        key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        if not key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not set in environment")
        return key

    @property
    def twilio_account_sid(self) -> str:
        """Get Twilio account SID."""
        return os.getenv('TWILIO_ACCOUNT_SID', '')

    @property
    def twilio_auth_token(self) -> str:
        """Get Twilio auth token."""
        return os.getenv('TWILIO_AUTH_TOKEN', '')

    @property
    def twilio_phone_number(self) -> str:
        """Get Twilio phone number."""
        return os.getenv('TWILIO_PHONE_NUMBER', '')

    @property
    def user_phone_number(self) -> str:
        """Get user phone number."""
        return os.getenv('USER_PHONE_NUMBER', '')

    @property
    def smtp_server(self) -> str:
        """Get SMTP server."""
        return os.getenv('SMTP_SERVER', 'smtp.gmail.com')

    @property
    def smtp_port(self) -> int:
        """Get SMTP port."""
        return int(os.getenv('SMTP_PORT', '587'))

    @property
    def email_address(self) -> str:
        """Get email address."""
        return os.getenv('EMAIL_ADDRESS', '')

    @property
    def email_password(self) -> str:
        """Get email password."""
        return os.getenv('EMAIL_PASSWORD', '')

    @property
    def recipient_email(self) -> str:
        """Get recipient email."""
        return os.getenv('RECIPIENT_EMAIL', '')

    @property
    def log_level(self) -> str:
        """Get log level."""
        return os.getenv('LOG_LEVEL', 'INFO')

    @property
    def timezone(self) -> str:
        """Get timezone."""
        return os.getenv('TIMEZONE', 'America/New_York')
