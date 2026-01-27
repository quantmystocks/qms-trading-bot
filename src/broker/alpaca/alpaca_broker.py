"""Alpaca broker implementation."""

import logging
from typing import List
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from ..broker import Broker
from ..models import Allocation

logger = logging.getLogger(__name__)


class AlpacaBroker(Broker):
    """Alpaca broker implementation."""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        """
        Initialize Alpaca broker.
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            base_url: Alpaca base URL (paper or live)
        """
        self.client = TradingClient(api_key=api_key, secret_key=api_secret, paper=base_url.startswith("https://paper"))
        logger.info(f"Initialized Alpaca broker (paper={base_url.startswith('https://paper')})")
    
    def get_current_allocation(self) -> List[Allocation]:
        """Get current portfolio allocation."""
        try:
            positions = self.client.get_all_positions()
            allocations = []
            
            for position in positions:
                allocations.append(Allocation(
                    symbol=position.symbol,
                    quantity=float(position.qty),
                    current_price=float(position.current_price),
                    market_value=float(position.market_value),
                ))
            
            logger.info(f"Retrieved {len(allocations)} positions from Alpaca")
            return allocations
        except Exception as e:
            logger.error(f"Error getting positions from Alpaca: {e}")
            raise
    
    def sell(self, symbol: str, quantity: float) -> bool:
        """Sell a stock."""
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
            order = self.client.submit_order(order_data=order_data)
            logger.info(f"Sold {quantity} shares of {symbol}. Order ID: {order.id}")
            return True
        except Exception as e:
            logger.error(f"Error selling {symbol}: {e}")
            return False
    
    def buy(self, symbol: str, amount: float) -> bool:
        """Buy a stock with a specific dollar amount."""
        try:
            # Get current price to calculate quantity
            asset = self.client.get_asset(symbol)
            if not asset.tradable:
                logger.error(f"Asset {symbol} is not tradable")
                return False
            
            # Get latest quote to determine price
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockLatestQuoteRequest
            
            # For simplicity, we'll use notional order (dollar amount)
            # Alpaca supports notional orders
            order_data = MarketOrderRequest(
                symbol=symbol,
                notional=amount,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )
            order = self.client.submit_order(order_data=order_data)
            logger.info(f"Bought ${amount} worth of {symbol}. Order ID: {order.id}")
            return True
        except Exception as e:
            logger.error(f"Error buying {symbol}: {e}")
            return False
    
    def get_account_cash(self) -> float:
        """Get available cash in the account."""
        try:
            account = self.client.get_account()
            return float(account.cash)
        except Exception as e:
            logger.error(f"Error getting account cash: {e}")
            raise
