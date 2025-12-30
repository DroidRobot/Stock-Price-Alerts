"""Basic import tests to verify package structure."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all modules can be imported."""
    from stock_alerts import config
    from stock_alerts import stock_api
    from stock_alerts import notifier
    from stock_alerts import database
    from stock_alerts import alerts
    from stock_alerts import logger
    from stock_alerts import cli

    assert config is not None
    assert stock_api is not None
    assert notifier is not None
    assert database is not None
    assert alerts is not None
    assert logger is not None
    assert cli is not None


if __name__ == "__main__":
    test_imports()
    print("✓ All imports successful")
