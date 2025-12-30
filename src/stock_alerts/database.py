"""Database management for storing stock price history."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class StockPrice(Base):
    """Stock price record model."""

    __tablename__ = 'stock_prices'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(Float, nullable=False)
    change = Column(Float)
    change_percent = Column(String(10))
    volume = Column(Integer)
    open_price = Column(Float)
    high = Column(Float)
    low = Column(Float)
    previous_close = Column(Float)
    timestamp = Column(DateTime, nullable=False, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'open_price': self.open_price,
            'high': self.high,
            'low': self.low,
            'previous_close': self.previous_close,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class StockDatabase:
    """Database manager for stock price history."""

    def __init__(self, database_url: str = "sqlite:///stock_data.db"):
        """Initialize database.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized: {database_url}")

    def _get_session(self) -> Session:
        """Get database session."""
        return self.Session()

    def save_quote(self, quote_data: Dict[str, Any]) -> bool:
        """Save stock quote to database.

        Args:
            quote_data: Quote data dictionary

        Returns:
            True if saved successfully
        """
        session = self._get_session()
        try:
            price_record = StockPrice(
                symbol=quote_data['symbol'],
                price=quote_data['price'],
                change=quote_data.get('change'),
                change_percent=quote_data.get('change_percent'),
                volume=quote_data.get('volume'),
                open_price=quote_data.get('open'),
                high=quote_data.get('high'),
                low=quote_data.get('low'),
                previous_close=quote_data.get('previous_close'),
                timestamp=datetime.fromisoformat(quote_data['timestamp'])
            )
            session.add(price_record)
            session.commit()
            logger.debug(f"Saved quote for {quote_data['symbol']} at {quote_data['price']}")
            return True

        except Exception as e:
            logger.error(f"Error saving quote: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_latest_price(self, symbol: str) -> Optional[StockPrice]:
        """Get latest price for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Latest StockPrice record or None
        """
        session = self._get_session()
        try:
            return session.query(StockPrice)\
                .filter(StockPrice.symbol == symbol)\
                .order_by(StockPrice.timestamp.desc())\
                .first()
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {e}")
            return None
        finally:
            session.close()

    def get_price_history(
        self,
        symbol: str,
        days: int = 7
    ) -> List[StockPrice]:
        """Get price history for a symbol.

        Args:
            symbol: Stock symbol
            days: Number of days of history to retrieve

        Returns:
            List of StockPrice records
        """
        session = self._get_session()
        try:
            since = datetime.now() - timedelta(days=days)
            return session.query(StockPrice)\
                .filter(StockPrice.symbol == symbol)\
                .filter(StockPrice.timestamp >= since)\
                .order_by(StockPrice.timestamp.desc())\
                .all()
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return []
        finally:
            session.close()

    def calculate_price_change(self, symbol: str, minutes: int = 15) -> Optional[float]:
        """Calculate price change percentage over a time period.

        Args:
            symbol: Stock symbol
            minutes: Time period in minutes

        Returns:
            Price change percentage or None
        """
        session = self._get_session()
        try:
            now = datetime.now()
            since = now - timedelta(minutes=minutes)

            latest = session.query(StockPrice)\
                .filter(StockPrice.symbol == symbol)\
                .order_by(StockPrice.timestamp.desc())\
                .first()

            oldest = session.query(StockPrice)\
                .filter(StockPrice.symbol == symbol)\
                .filter(StockPrice.timestamp >= since)\
                .order_by(StockPrice.timestamp.asc())\
                .first()

            if not latest or not oldest or oldest.price == 0:
                return None

            change_percent = ((latest.price - oldest.price) / oldest.price) * 100
            return round(change_percent, 2)

        except Exception as e:
            logger.error(f"Error calculating price change for {symbol}: {e}")
            return None
        finally:
            session.close()

    def cleanup_old_data(self, retention_days: int = 90) -> int:
        """Remove old price data.

        Args:
            retention_days: Number of days to keep

        Returns:
            Number of records deleted
        """
        session = self._get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted = session.query(StockPrice)\
                .filter(StockPrice.timestamp < cutoff_date)\
                .delete()
            session.commit()
            logger.info(f"Cleaned up {deleted} old price records")
            return deleted
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            session.rollback()
            return 0
        finally:
            session.close()
