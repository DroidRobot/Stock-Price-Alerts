"""Alpha Vantage API wrapper for fetching stock data."""

import requests
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StockAPIError(Exception):
    """Exception raised for stock API errors."""
    pass


class StockAPI:
    """Wrapper for Alpha Vantage API."""

    BASE_URL = 'https://www.alphavantage.co/query'

    def __init__(self, api_key: str, retry_count: int = 3, retry_delay: int = 12):
        """Initialize Stock API.

        Args:
            api_key: Alpha Vantage API key
            retry_count: Number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make API request with retry logic.

        Args:
            params: Request parameters

        Returns:
            API response as dictionary

        Raises:
            StockAPIError: If request fails after retries
        """
        params['apikey'] = self.api_key

        for attempt in range(self.retry_count):
            try:
                response = requests.get(self.BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # Check for API errors
                if 'Error Message' in data:
                    raise StockAPIError(f"API Error: {data['Error Message']}")

                if 'Note' in data:
                    logger.warning(f"API Rate limit: {data['Note']}")
                    if attempt < self.retry_count - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    raise StockAPIError("API rate limit exceeded")

                return data

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise StockAPIError(f"Failed to fetch data after {self.retry_count} attempts: {e}")

        raise StockAPIError("Failed to fetch data")

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current stock quote.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Dictionary containing stock quote data or None if failed
        """
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            }

            data = self._make_request(params)

            if 'Global Quote' not in data or not data['Global Quote']:
                logger.error(f"No quote data found for {symbol}")
                return None

            quote = data['Global Quote']

            # Parse and format the data
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').rstrip('%'),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day', ''),
                'previous_close': float(quote.get('08. previous close', 0)),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'timestamp': datetime.now().isoformat()
            }

        except StockAPIError as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing quote data for {symbol}: {e}")
            return None

    def get_intraday(self, symbol: str, interval: str = '5min') -> Optional[Dict[str, Any]]:
        """Get intraday time series data.

        Args:
            symbol: Stock symbol
            interval: Time interval (1min, 5min, 15min, 30min, 60min)

        Returns:
            Dictionary containing intraday data or None if failed
        """
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval
            }

            data = self._make_request(params)

            time_series_key = f'Time Series ({interval})'
            if time_series_key not in data:
                logger.error(f"No intraday data found for {symbol}")
                return None

            return data[time_series_key]

        except StockAPIError as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None

    def get_price(self, symbol: str) -> Optional[float]:
        """Get current stock price (simplified method).

        Args:
            symbol: Stock symbol

        Returns:
            Current price or None if failed
        """
        quote = self.get_quote(symbol)
        return quote['price'] if quote else None
