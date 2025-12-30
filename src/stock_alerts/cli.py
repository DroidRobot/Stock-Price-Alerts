"""Command-line interface for Stock Price Alerts."""

import click
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .config import Config
from .stock_api import StockAPI
from .database import StockDatabase

console = Console()


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """Stock Price Alerts - Monitor and get notified about stock price changes."""
    pass


@cli.command()
@click.argument('symbol')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def add(symbol: str, config: str):
    """Add a stock symbol to the watchlist.

    Example: stock-alerts add AAPL
    """
    symbol = symbol.upper()
    config_path = Path(config)

    if not config_path.exists():
        console.print(f"[red]Error: Configuration file not found: {config}[/red]")
        return

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    watchlist = config_data.get('watchlist', [])

    if symbol in watchlist:
        console.print(f"[yellow]{symbol} is already in the watchlist[/yellow]")
        return

    watchlist.append(symbol)
    config_data['watchlist'] = watchlist

    with open(config_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)

    console.print(f"[green]✓ Added {symbol} to watchlist[/green]")


@cli.command()
@click.argument('symbol')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def remove(symbol: str, config: str):
    """Remove a stock symbol from the watchlist.

    Example: stock-alerts remove AAPL
    """
    symbol = symbol.upper()
    config_path = Path(config)

    if not config_path.exists():
        console.print(f"[red]Error: Configuration file not found: {config}[/red]")
        return

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    watchlist = config_data.get('watchlist', [])

    if symbol not in watchlist:
        console.print(f"[yellow]{symbol} is not in the watchlist[/yellow]")
        return

    watchlist.remove(symbol)
    config_data['watchlist'] = watchlist

    with open(config_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)

    console.print(f"[green]✓ Removed {symbol} from watchlist[/green]")


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def list(config: str):
    """List all stocks in the watchlist.

    Example: stock-alerts list
    """
    try:
        cfg = Config(config)
        watchlist = cfg.get_watchlist()

        if not watchlist:
            console.print("[yellow]Watchlist is empty[/yellow]")
            return

        console.print("\n[bold]Current Watchlist:[/bold]")
        for symbol in watchlist:
            console.print(f"  • {symbol}")
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('symbol')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def quote(symbol: str, config: str):
    """Get current quote for a stock symbol.

    Example: stock-alerts quote AAPL
    """
    try:
        symbol = symbol.upper()
        cfg = Config(config)
        api = StockAPI(cfg.alpha_vantage_api_key)

        console.print(f"\n[bold]Fetching quote for {symbol}...[/bold]")
        quote_data = api.get_quote(symbol)

        if not quote_data:
            console.print(f"[red]Failed to fetch quote for {symbol}[/red]")
            return

        # Display quote in a nice table
        table = Table(title=f"{symbol} Quote")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Price", f"${quote_data['price']:.2f}")
        table.add_row("Change", f"${quote_data['change']:.2f}")
        table.add_row("Change %", f"{quote_data['change_percent']}%")
        table.add_row("Volume", f"{quote_data['volume']:,}")
        table.add_row("Open", f"${quote_data['open']:.2f}")
        table.add_row("High", f"${quote_data['high']:.2f}")
        table.add_row("Low", f"${quote_data['low']:.2f}")
        table.add_row("Previous Close", f"${quote_data['previous_close']:.2f}")

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def prices(config: str):
    """Get current prices for all stocks in watchlist.

    Example: stock-alerts prices
    """
    try:
        cfg = Config(config)
        watchlist = cfg.get_watchlist()

        if not watchlist:
            console.print("[yellow]Watchlist is empty[/yellow]")
            return

        api = StockAPI(cfg.alpha_vantage_api_key)
        rate_limit = cfg.get_rate_limiting_config().get('api_delay', 12)

        table = Table(title="Watchlist Prices")
        table.add_column("Symbol", style="cyan")
        table.add_column("Price", style="green")
        table.add_column("Change", style="yellow")
        table.add_column("Change %", style="yellow")
        table.add_column("Volume", style="blue")

        import time
        for i, symbol in enumerate(watchlist):
            quote = api.get_quote(symbol)
            if quote:
                change_style = "green" if quote['change'] >= 0 else "red"
                table.add_row(
                    symbol,
                    f"${quote['price']:.2f}",
                    f"[{change_style}]${quote['change']:.2f}[/{change_style}]",
                    f"[{change_style}]{quote['change_percent']}%[/{change_style}]",
                    f"{quote['volume']:,}"
                )
            else:
                table.add_row(symbol, "N/A", "N/A", "N/A", "N/A")

            # Rate limiting
            if i < len(watchlist) - 1:
                time.sleep(rate_limit)

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('symbol')
@click.option('--days', '-d', default=7, help='Number of days of history')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def history(symbol: str, days: int, config: str):
    """Show price history for a stock symbol.

    Example: stock-alerts history AAPL --days 7
    """
    try:
        symbol = symbol.upper()
        cfg = Config(config)
        storage_config = cfg.get_storage_config()

        if not storage_config.get('enabled'):
            console.print("[yellow]Storage is disabled in configuration[/yellow]")
            return

        db = StockDatabase(f"sqlite:///{storage_config.get('database', 'stock_data.db')}")
        history_data = db.get_price_history(symbol, days)

        if not history_data:
            console.print(f"[yellow]No history found for {symbol}[/yellow]")
            return

        table = Table(title=f"{symbol} Price History ({days} days)")
        table.add_column("Date/Time", style="cyan")
        table.add_column("Price", style="green")
        table.add_column("Change", style="yellow")
        table.add_column("Volume", style="blue")

        for record in history_data[:20]:  # Show last 20 records
            change_style = "green" if (record.change or 0) >= 0 else "red"
            table.add_row(
                record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                f"${record.price:.2f}",
                f"[{change_style}]{record.change_percent}%[/{change_style}]" if record.change_percent else "N/A",
                f"{record.volume:,}" if record.volume else "N/A"
            )

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def test(config: str):
    """Test notification configuration.

    Example: stock-alerts test
    """
    try:
        cfg = Config(config)
        from .notifier import SMSNotifier, EmailNotifier

        notifications_config = cfg.get_notifications_config()
        console.print("\n[bold]Testing Notifications...[/bold]\n")

        # Test SMS
        if notifications_config.get('sms_enabled'):
            console.print("[cyan]Testing SMS notification...[/cyan]")
            sms = SMSNotifier(
                cfg.twilio_account_sid,
                cfg.twilio_auth_token,
                cfg.twilio_phone_number,
                cfg.user_phone_number
            )
            if sms.send("Test message from Stock Price Alerts"):
                console.print("[green]✓ SMS sent successfully[/green]")
            else:
                console.print("[red]✗ SMS failed[/red]")
        else:
            console.print("[yellow]SMS notifications disabled[/yellow]")

        # Test Email
        if notifications_config.get('email_enabled'):
            console.print("\n[cyan]Testing email notification...[/cyan]")
            email = EmailNotifier(
                cfg.smtp_server,
                cfg.smtp_port,
                cfg.email_address,
                cfg.email_password,
                cfg.recipient_email
            )
            if email.send("Test Email", "Test message from Stock Price Alerts"):
                console.print("[green]✓ Email sent successfully[/green]")
            else:
                console.print("[red]✗ Email failed[/red]")
        else:
            console.print("[yellow]Email notifications disabled[/yellow]")

        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()
