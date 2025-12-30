# Stock Price Alerts 📈

A comprehensive, modern stock monitoring and alerting system that sends you notifications via SMS and email based on scheduled times and significant price changes.

## Features 

- **Multi-Channel Notifications**: Send alerts via SMS (Twilio) and Email
- **Scheduled Alerts**: Get updates at market open, noon, and close (fully customizable)
- **Price Change Alerts**: Automatic notifications when stocks move by a threshold percentage
- **Historical Data**: Store and track price history in a SQLite database
- **Beautiful CLI**: Rich command-line interface for managing your watchlist
- **Highly Configurable**: YAML-based configuration for all settings
- **Secure**: Environment variables for sensitive credentials
- **Real-time Monitoring**: Continuous monitoring with intelligent rate limiting
- **Timezone Support**: Configurable timezone for market hours
- **Robust Error Handling**: Automatic retries and comprehensive logging

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Alpha Vantage API key (free at [alphavantage.co](https://www.alphavantage.co/support/#api-key))
- Twilio account (optional, for SMS) from [twilio.com](https://www.twilio.com)
- SMTP email account (optional, for email alerts)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Stock-Price-Alerts.git
   cd Stock-Price-Alerts
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install as a package:
   ```bash
   pip install -e .
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=+1234567890
   USER_PHONE_NUMBER=+1234567890
   ```

4. **Customize your watchlist**

   Edit `config.yaml` and add your favorite stocks:
   ```yaml
   watchlist:
     - AAPL
     - GOOGL
     - MSFT
     - TSLA
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Configuration

### config.yaml

The main configuration file controls all aspects of the application:

```yaml
# Stocks to monitor
watchlist:
  - AAPL
  - GOOGL
  - MSFT

# Alert schedule (24-hour format)
alert_schedule:
  - time: "09:30"
    message: "Market is open!"
  - time: "16:00"
    message: "Market is closing!"

# Price change alerts
price_alerts:
  enabled: true
  threshold_percentage: 5.0  # Alert on 5% change
  check_interval: 15         # Check every 15 minutes

# Notification settings
notifications:
  sms_enabled: true
  email_enabled: false
  include_price_change: true
  include_volume: true
  include_day_high_low: true

# Market hours (Eastern Time)
market_hours:
  open: "09:30"
  close: "16:00"
  only_during_market_hours: false

# Data storage
storage:
  enabled: true
  database: "stock_data.db"
  retention_days: 90

# API rate limiting
rate_limiting:
  api_delay: 12       # Seconds between API calls
  max_retries: 3
```

### .env

Store your sensitive credentials in the `.env` file:

```env
# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_key_here

# Twilio (SMS)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
USER_PHONE_NUMBER=+1234567890

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com

# Application
LOG_LEVEL=INFO
TIMEZONE=America/New_York
```

## CLI Commands

The application includes a powerful CLI for managing your watchlist:

### Add a stock to watchlist
```bash
python -m stock_alerts.cli add AAPL
```

### Remove a stock from watchlist
```bash
python -m stock_alerts.cli remove AAPL
```

### List all stocks in watchlist
```bash
python -m stock_alerts.cli list
```

### Get current quote for a stock
```bash
python -m stock_alerts.cli quote AAPL
```

### Get prices for all stocks in watchlist
```bash
python -m stock_alerts.cli prices
```

### View price history
```bash
python -m stock_alerts.cli history AAPL --days 7
```

### Test notifications
```bash
python -m stock_alerts.cli test
```

## Usage Examples

### Basic Usage

1. **Start monitoring:**
   ```bash
   python main.py
   ```

2. **The application will:**
   - Monitor all stocks in your watchlist
   - Send scheduled alerts at configured times
   - Send alerts when prices change by threshold percentage
   - Store price history in the database
   - Log all activities

### Advanced Usage

**Only monitor during market hours:**
```yaml
market_hours:
  only_during_market_hours: true
```

**Aggressive price monitoring:**
```yaml
price_alerts:
  threshold_percentage: 2.0  # Alert on 2% change
  check_interval: 5          # Check every 5 minutes
```

**Email-only notifications:**
```yaml
notifications:
  sms_enabled: false
  email_enabled: true
```

## Project Structure

```
Stock-Price-Alerts/
├── main.py                      # Main entry point
├── config.yaml                  # Configuration file
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── src/
│   └── stock_alerts/
│       ├── __init__.py         # Package init
│       ├── config.py           # Configuration loader
│       ├── stock_api.py        # Alpha Vantage API wrapper
│       ├── notifier.py         # SMS & Email notifications
│       ├── database.py         # SQLite database management
│       ├── alerts.py           # Alert logic & monitoring
│       ├── logger.py           # Logging configuration
│       └── cli.py              # Command-line interface
├── tests/                       # Unit tests (future)
└── logs/                        # Application logs
```

## How It Works

1. **Configuration Loading**: Reads `config.yaml` and `.env` files
2. **Initialization**: Sets up API clients, database, and notifiers
3. **Monitoring Loop**:
   - Checks every minute for scheduled alerts
   - Periodically checks for significant price changes
   - Fetches current stock data from Alpha Vantage API
   - Stores data in SQLite database
4. **Alert Processing**:
   - Formats stock data into readable messages
   - Sends via configured notification channels (SMS/Email)
   - Tracks alerts to avoid duplicates
5. **Data Management**:
   - Stores historical prices
   - Calculates price changes
   - Cleans up old data based on retention settings

## API Rate Limits

**Alpha Vantage Free Tier:**
- 5 API calls per minute
- 500 API calls per day

The application automatically handles rate limiting with configurable delays between requests.

## Security 🔒

- **Never commit `.env` file** - it contains sensitive credentials
- Use `.env.example` as a template
- API keys and passwords are loaded from environment variables
- Database files are excluded from git

## Troubleshooting

### Common Issues

**"ALPHA_VANTAGE_API_KEY not set"**
- Make sure you've created a `.env` file from `.env.example`
- Add your API key to the `.env` file

**"Failed to fetch data"**
- Check your internet connection
- Verify your Alpha Vantage API key is valid
- You may have hit the API rate limit (wait a minute)

**"SMS/Email not sending"**
- Verify your Twilio/SMTP credentials in `.env`
- Run `python -m stock_alerts.cli test` to test notifications
- Check the logs in `logs/stock_alerts.log`

**"Watchlist is empty"**
- Add stocks to `config.yaml` under the `watchlist` section
- Or use CLI: `python -m stock_alerts.cli add AAPL`

### Logging

Logs are stored in `logs/stock_alerts.log`. Check this file for detailed error messages and debugging information.

Set log level in `.env`:
```env
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR
```

## Upgrading from v1

If you're using the original `main.py`, here's what's new:

**v1 → v2 Changes:**
- Modular architecture (organized code)
- Environment variables (secure credentials)
- Email notifications (in addition to SMS)
- Price change alerts (dynamic monitoring)
- Database storage (price history)
- CLI interface (easy management)
- Better error handling (robust)
- Comprehensive logging (debugging)
- YAML configuration (flexible)
- Fixed time checking (reliable alerts)

## Contributing 🤝

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License 📄

This project is open source and available for personal and educational use.

## Acknowledgments 🙏

- [Alpha Vantage](https://www.alphavantage.co/) for stock market data API
- [Twilio](https://www.twilio.com/) for SMS messaging API
- Built with ❤️ using Python

## Support 💬

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the logs in `logs/stock_alerts.log`
3. Open an issue on GitHub

---

**Happy Trading! 📈💰**

