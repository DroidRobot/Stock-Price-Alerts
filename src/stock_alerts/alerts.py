"""Alert management and monitoring logic."""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import pytz
from .config import Config
from .stock_api import StockAPI
from .notifier import Notifier
from .database import StockDatabase

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages stock price alerts and monitoring."""

    def __init__(
        self,
        config: Config,
        stock_api: StockAPI,
        notifier: Notifier,
        database: Optional[StockDatabase] = None
    ):
        """Initialize alert manager.

        Args:
            config: Configuration instance
            stock_api: Stock API instance
            notifier: Notifier instance
            database: Database instance (optional)
        """
        self.config = config
        self.stock_api = stock_api
        self.notifier = notifier
        self.database = database
        self.timezone = pytz.timezone(config.timezone)

        # Track last alert times to avoid duplicates
        self.last_scheduled_alerts: Dict[str, datetime] = {}
        self.last_price_alerts: Dict[str, datetime] = {}

    def format_stock_message(self, quote: Dict[str, Any], include_details: bool = True) -> str:
        """Format stock quote into a readable message.

        Args:
            quote: Stock quote data
            include_details: Whether to include detailed information

        Returns:
            Formatted message string
        """
        symbol = quote['symbol']
        price = quote['price']
        change = quote.get('change', 0)
        change_percent = quote.get('change_percent', '0')

        # Basic message
        message = f"{symbol}: ${price:.2f}"

        if include_details:
            # Add change information
            change_symbol = "+" if change >= 0 else ""
            message += f" ({change_symbol}${change:.2f}, {change_symbol}{change_percent}%)"

            # Add volume if available
            notifications_config = self.config.get_notifications_config()
            if notifications_config.get('include_volume') and quote.get('volume'):
                volume = quote['volume']
                message += f" | Vol: {volume:,}"

            # Add high/low if available
            if notifications_config.get('include_day_high_low'):
                if quote.get('high') and quote.get('low'):
                    message += f" | H: ${quote['high']:.2f} L: ${quote['low']:.2f}"

        return message

    def get_current_time(self) -> datetime:
        """Get current time in configured timezone.

        Returns:
            Current datetime with timezone
        """
        return datetime.now(self.timezone)

    def is_market_hours(self) -> bool:
        """Check if current time is within market hours.

        Returns:
            True if within market hours
        """
        market_hours = self.config.get_market_hours()
        if not market_hours.get('only_during_market_hours', False):
            return True

        now = self.get_current_time()
        current_time = now.time()

        open_time = datetime.strptime(market_hours['open'], '%H:%M').time()
        close_time = datetime.strptime(market_hours['close'], '%H:%M').time()

        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Weekend
            return False

        return open_time <= current_time <= close_time

    def check_scheduled_alerts(self) -> None:
        """Check and send scheduled time-based alerts."""
        now = self.get_current_time()
        current_time = now.strftime('%H:%M')

        alert_schedule = self.config.get_alert_schedule()
        watchlist = self.config.get_watchlist()

        if not watchlist:
            logger.warning("Watchlist is empty, skipping scheduled alerts")
            return

        for schedule_item in alert_schedule:
            alert_time = schedule_item['time']
            alert_message = schedule_item['message']

            # Check if it's time for this alert
            if current_time == alert_time:
                # Avoid sending duplicate alerts within the same minute
                alert_key = f"{alert_time}_{now.date()}"
                if alert_key in self.last_scheduled_alerts:
                    logger.debug(f"Already sent alert for {alert_time} today")
                    continue

                logger.info(f"Sending scheduled alert for {alert_time}")
                self._send_watchlist_alert(alert_message)
                self.last_scheduled_alerts[alert_key] = now

    def _send_watchlist_alert(self, intro_message: str) -> None:
        """Send alert with watchlist stock prices.

        Args:
            intro_message: Introduction message for the alert
        """
        watchlist = self.config.get_watchlist()
        rate_limit_config = self.config.get_rate_limiting_config()
        api_delay = rate_limit_config.get('api_delay', 12)

        messages = [intro_message]

        for i, symbol in enumerate(watchlist):
            quote = self.stock_api.get_quote(symbol)

            if quote:
                # Save to database if enabled
                if self.database:
                    self.database.save_quote(quote)

                # Format and add to messages
                stock_msg = self.format_stock_message(quote)
                messages.append(stock_msg)
            else:
                messages.append(f"{symbol}: Unable to fetch price")

            # Rate limiting - delay between API calls
            if i < len(watchlist) - 1:
                time.sleep(api_delay)

        # Send combined message
        full_message = "\n".join(messages)
        self.notifier.notify(full_message)

    def check_price_change_alerts(self) -> None:
        """Check for significant price changes and send alerts."""
        price_alerts_config = self.config.get_price_alerts_config()

        if not price_alerts_config.get('enabled', False):
            return

        threshold = price_alerts_config.get('threshold_percentage', 5.0)
        check_interval = price_alerts_config.get('check_interval', 15)
        watchlist = self.config.get_watchlist()

        if not watchlist or not self.database:
            return

        for symbol in watchlist:
            # Get current price
            quote = self.stock_api.get_quote(symbol)
            if not quote:
                continue

            # Save current price
            self.database.save_quote(quote)

            # Calculate price change over the check interval
            price_change = self.database.calculate_price_change(symbol, check_interval)

            if price_change is None:
                continue

            # Check if change exceeds threshold
            if abs(price_change) >= threshold:
                # Avoid duplicate alerts
                alert_key = f"{symbol}_{datetime.now().strftime('%Y-%m-%d_%H')}"
                if alert_key in self.last_price_alerts:
                    continue

                # Send alert
                direction = "up" if price_change > 0 else "down"
                alert_msg = (
                    f"🚨 PRICE ALERT 🚨\n"
                    f"{symbol} is {direction} {abs(price_change):.2f}% "
                    f"in the last {check_interval} minutes!\n"
                    f"{self.format_stock_message(quote)}"
                )

                logger.info(f"Sending price change alert for {symbol}")
                self.notifier.notify(alert_msg, subject=f"Price Alert: {symbol}")
                self.last_price_alerts[alert_key] = datetime.now()

            # Rate limiting
            time.sleep(self.config.get_rate_limiting_config().get('api_delay', 12))

    def run_monitoring_cycle(self) -> None:
        """Run one monitoring cycle - check all alerts."""
        try:
            logger.debug("Running monitoring cycle")

            # Check if we should run (market hours check)
            market_hours = self.config.get_market_hours()
            if market_hours.get('only_during_market_hours', False):
                if not self.is_market_hours():
                    logger.debug("Outside market hours, skipping monitoring")
                    return

            # Check scheduled alerts
            self.check_scheduled_alerts()

            # Check price change alerts
            self.check_price_change_alerts()

            # Cleanup old database records periodically
            if self.database:
                now = self.get_current_time()
                if now.hour == 0 and now.minute == 0:  # Once a day at midnight
                    retention_days = self.config.get_storage_config().get('retention_days', 90)
                    self.database.cleanup_old_data(retention_days)

        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}", exc_info=True)
