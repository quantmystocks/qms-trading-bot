"""Abstract base class for broker implementations."""

from abc import ABC, abstractmethod
from typing import List
from .models import Allocation


class Broker(ABC):
    """Abstract base class for broker implementations."""
    
    @abstractmethod
    def get_current_allocation(self) -> List[Allocation]:
        """
        Get current portfolio allocation.
        
        Returns:
            List of Allocation objects representing current positions.
        """
        pass
    
    @abstractmethod
    def sell(self, symbol: str, quantity: float) -> bool:
        """
        Sell a stock.
        
        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell
            
        Returns:
            True if order was placed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def buy(self, symbol: str, amount: float) -> bool:
        """
        Buy a stock with a specific dollar amount.
        
        Args:
            symbol: Stock symbol to buy
            amount: Dollar amount to spend
            
        Returns:
            True if order was placed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_account_cash(self) -> float:
        """
        Get available cash in the account.
        
        Returns:
            Available cash amount
        """
        pass
