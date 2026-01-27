"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List

from src.broker.models import Allocation
from src.broker.broker import Broker
from src.leaderboard import LeaderboardClient
from src.notifications import EmailNotifier


@pytest.fixture
def mock_allocation():
    """Create a mock allocation."""
    return Allocation(
        symbol="AAPL",
        quantity=10.0,
        current_price=150.0,
        market_value=1500.0,
    )


@pytest.fixture
def mock_allocations():
    """Create mock allocations."""
    return [
        Allocation(symbol="AAPL", quantity=10.0, current_price=150.0, market_value=1500.0),
        Allocation(symbol="MSFT", quantity=5.0, current_price=300.0, market_value=1500.0),
        Allocation(symbol="GOOGL", quantity=3.0, current_price=100.0, market_value=300.0),
    ]


@pytest.fixture
def mock_broker():
    """Create a mock broker."""
    broker = Mock(spec=Broker)
    broker.get_current_allocation.return_value = []
    broker.sell.return_value = True
    broker.buy.return_value = True
    broker.get_account_cash.return_value = 10000.0
    return broker


@pytest.fixture
def mock_leaderboard_client():
    """Create a mock leaderboard client."""
    client = Mock(spec=LeaderboardClient)
    client.get_top_symbols.return_value = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    return client


@pytest.fixture
def mock_email_notifier():
    """Create a mock email notifier."""
    notifier = Mock(spec=EmailNotifier)
    notifier.send_trade_summary.return_value = True
    notifier.send_error_notification.return_value = True
    return notifier
