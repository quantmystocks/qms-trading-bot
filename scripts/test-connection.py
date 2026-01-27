#!/usr/bin/env python3
"""Test connections to broker and leaderboard API."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.broker import create_broker
from src.leaderboard import LeaderboardClient


def test_connections():
    """Test all connections."""
    print("Testing connections...")
    print("=" * 60)
    
    config = get_config()
    all_passed = True
    
    # Test leaderboard API
    print("\n1. Testing Leaderboard API...")
    try:
        client = LeaderboardClient(
            api_url=config.leaderboard_api_url,
            api_token=config.leaderboard_api_token,
        )
        symbols = client.get_top_symbols(top_n=5)
        print(f"   ✓ Connected successfully")
        print(f"   ✓ Retrieved {len(symbols)} symbols: {', '.join(symbols)}")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        all_passed = False
    
    # Test broker
    print(f"\n2. Testing {config.broker.broker_type.upper()} Broker...")
    try:
        broker = create_broker()
        cash = broker.get_account_cash()
        positions = broker.get_current_allocation()
        print(f"   ✓ Connected successfully")
        print(f"   ✓ Account cash: ${cash:,.2f}")
        print(f"   ✓ Current positions: {len(positions)}")
        if positions:
            for pos in positions:
                print(f"     - {pos.symbol}: {pos.quantity:.2f} shares @ ${pos.current_price:.2f}")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        all_passed = False
    
    # Test email (if enabled)
    if config.email.enabled:
        print(f"\n3. Testing Email ({config.email.provider.upper()})...")
        try:
            from src.notifications import create_email_notifier
            notifier = create_email_notifier()
            if notifier:
                print(f"   ✓ Email notifier created successfully")
                print(f"   Note: Actual email sending will be tested during rebalancing")
            else:
                print(f"   ⚠ Email notifier could not be created")
        except Exception as e:
            print(f"   ✗ Email setup failed: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All connections successful!")
        return 0
    else:
        print("✗ Some connections failed. Please check your configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(test_connections())
