# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your favorite editor
```

Required credentials:
- **Alpha Vantage API Key**: Get free at https://www.alphavantage.co/support/#api-key
- **Twilio** (optional for SMS): Sign up at https://www.twilio.com
- **Email** (optional): Use your Gmail or other SMTP server

## Step 3: Configure Watchlist

Edit `config.yaml` and add stocks you want to monitor:

```yaml
watchlist:
  - AAPL
  - GOOGL
  - MSFT
  - TSLA
```

## Step 4: Run the Application

```bash
python main.py
```

The application will:
- Start monitoring your stocks
- Send alerts at scheduled times
- Alert you on significant price changes
- Store historical data

## CLI Commands

```bash
# Add a stock
python -m stock_alerts.cli add NVDA

# Remove a stock
python -m stock_alerts.cli remove NVDA

# View all stocks
python -m stock_alerts.cli list

# Get current prices
python -m stock_alerts.cli prices

# Get a quote
python -m stock_alerts.cli quote AAPL

# View history
python -m stock_alerts.cli history AAPL --days 7

# Test notifications
python -m stock_alerts.cli test
```

## Troubleshooting

**Import Errors?**
```bash
pip install -r requirements.txt
```

**API Key Issues?**
- Make sure `.env` file exists (copy from `.env.example`)
- Verify your Alpha Vantage API key is correct

**No Alerts?**
- Check `config.yaml` - is your watchlist populated?
- Check alert schedule times
- Review logs in `logs/stock_alerts.log`

## What's Next?

- Customize alert times in `config.yaml`
- Enable email notifications
- Set price change thresholds
- Configure market hours monitoring

For full documentation, see [README.md](README.md)
