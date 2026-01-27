"""Robinhood broker implementation."""

import logging
from typing import List, Optional
import robin_stocks.robinhood as rh

from ..broker import Broker
from ..models import Allocation

logger = logging.getLogger(__name__)


class RobinhoodBroker(Broker):
    """Robinhood broker implementation."""
    
    def __init__(self, username: str, password: str, mfa_code: Optional[str] = None):
        """
        Initialize Robinhood broker.
        
        Args:
            username: Robinhood username/email
            password: Robinhood password
            mfa_code: Optional MFA code if 2FA is enabled
        """
        try:
            if mfa_code:
                rh.login(username=username, password=password, mfa_code=mfa_code)
            else:
                rh.login(username=username, password=password)
            logger.info("Successfully logged into Robinhood")
        except Exception as e:
            logger.error(f"Error logging into Robinhood: {e}")
            raise
    
    def get_current_allocation(self) -> List[Allocation]:
        """Get current portfolio allocation."""
        try:
            positions = rh.get_open_stock_positions()
            allocations = []
            
            for position in positions:
                symbol = position.get("symbol")
                quantity = float(position.get("quantity", 0))
                
                if quantity > 0 and symbol:
                    # Get current price
                    quote = rh.get_quotes(symbol)[0] if rh.get_quotes(symbol) else None
                    if quote:
                        current_price = float(quote.get("last_trade_price", 0))
                        market_value = quantity * current_price
                        
                        allocations.append(Allocation(
                            symbol=symbol,
                            quantity=quantity,
                            current_price=current_price,
                            market_value=market_value,
                        ))
            
            logger.info(f"Retrieved {len(allocations)} positions from Robinhood")
            return allocations
        except Exception as e:
            logger.error(f"Error getting positions from Robinhood: {e}")
            raise
    
    def sell(self, symbol: str, quantity: float) -> bool:
        """Sell a stock."""
        try:
            order = rh.order_sell_market(symbol=symbol, quantity=quantity)
            if order and order.get("id"):
                logger.info(f"Sold {quantity} shares of {symbol}. Order ID: {order.get('id')}")
                return True
            else:
                logger.error(f"Failed to sell {symbol}: {order}")
                return False
        except Exception as e:
            logger.error(f"Error selling {symbol}: {e}")
            return False
    
    def buy(self, symbol: str, amount: float) -> bool:
        """Buy a stock with a specific dollar amount."""
        try:
            # Get current price to calculate quantity
            quote = rh.get_quotes(symbol)
            if not quote:
                logger.error(f"Could not get quote for {symbol}")
                return False
            
            current_price = float(quote[0].get("last_trade_price", 0))
            if current_price == 0:
                logger.error(f"Invalid price for {symbol}")
                return False
            
            quantity = amount / current_price
            order = rh.order_buy_market(symbol=symbol, quantity=quantity)
            
            if order and order.get("id"):
                logger.info(f"Bought ${amount} worth of {symbol} ({quantity} shares). Order ID: {order.get('id')}")
                return True
            else:
                logger.error(f"Failed to buy {symbol}: {order}")
                return False
        except Exception as e:
            logger.error(f"Error buying {symbol}: {e}")
            return False
    
    def get_account_cash(self) -> float:
        """Get available cash in the account."""
        try:
            profile = rh.load_account_profile()
            cash = float(profile.get("cash", 0))
            return cash
        except Exception as e:
            logger.error(f"Error getting account cash: {e}")
            raise
