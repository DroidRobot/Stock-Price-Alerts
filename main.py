#!/usr/bin/env python3
"""
Stock Price Alerts - Main Entry Point

A comprehensive stock monitoring and alerting system that sends notifications
via SMS and email based on scheduled times and price changes.
"""

import sys
import time
import logging
import signal
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stock_alerts.config import Config
from stock_alerts.stock_api import StockAPI
from stock_alerts.notifier import Notifier, SMSNotifier, EmailNotifier
from stock_alerts.database import StockDatabase
from stock_alerts.alerts import AlertManager
from stock_alerts.logger import setup_logging

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info("Received shutdown signal, stopping...")
    running = False


def main():
    """Main application entry point."""
    global running

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Load configuration
        logger.info("Starting Stock Price Alerts v2.0.0")
        config = Config()

        # Setup logging
        setup_logging(
            log_level=config.log_level,
            log_file="logs/stock_alerts.log"
        )

        # Validate watchlist
        watchlist = config.get_watchlist()
        if not watchlist:
            logger.warning("Watchlist is empty! Add stocks to config.yaml or use the CLI:")
            logger.warning("  python -m stock_alerts.cli add AAPL")
            logger.info("Continuing to run, but no alerts will be sent...")

        # Initialize components
        logger.info("Initializing components...")

        # Stock API
        stock_api = StockAPI(
            api_key=config.alpha_vantage_api_key,
            retry_count=config.get_rate_limiting_config().get('max_retries', 3),
            retry_delay=config.get_rate_limiting_config().get('api_delay', 12)
        )

        # Notifiers
        notifications_config = config.get_notifications_config()

        sms_notifier = SMSNotifier(
            account_sid=config.twilio_account_sid,
            auth_token=config.twilio_auth_token,
            from_number=config.twilio_phone_number,
            to_number=config.user_phone_number
        )

        email_notifier = EmailNotifier(
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port,
            email_address=config.email_address,
            email_password=config.email_password,
            recipient_email=config.recipient_email
        )

        notifier = Notifier(
            sms_notifier=sms_notifier,
            email_notifier=email_notifier,
            sms_enabled=notifications_config.get('sms_enabled', True),
            email_enabled=notifications_config.get('email_enabled', False)
        )

        # Database (optional)
        database = None
        storage_config = config.get_storage_config()
        if storage_config.get('enabled', True):
            database = StockDatabase(
                database_url=f"sqlite:///{storage_config.get('database', 'stock_data.db')}"
            )
            logger.info("Database storage enabled")

        # Alert Manager
        alert_manager = AlertManager(
            config=config,
            stock_api=stock_api,
            notifier=notifier,
            database=database
        )

        logger.info("All components initialized successfully")
        logger.info(f"Monitoring {len(watchlist)} stocks: {', '.join(watchlist)}")
        logger.info("Press Ctrl+C to stop")

        # Main monitoring loop
        while running:
            try:
                alert_manager.run_monitoring_cycle()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(60)

        logger.info("Application stopped")

    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Make sure config.yaml exists. Copy config.yaml.example if needed.")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Make sure all required environment variables are set in .env file")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()