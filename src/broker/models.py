"""Data models for broker positions and allocations."""

from dataclasses import dataclass
from typing import List


@dataclass
class Allocation:
    """Represents a stock position in the portfolio."""
    
    symbol: str
    quantity: float
    current_price: float
    market_value: float
    
    def __eq__(self, other: object) -> bool:
        """Compare allocations by symbol."""
        if not isinstance(other, Allocation):
            return False
        return self.symbol.upper() == other.symbol.upper()
    
    def __hash__(self) -> int:
        """Hash by symbol."""
        return hash(self.symbol.upper())


@dataclass
class TradeSummary:
    """Summary of trades executed during rebalancing."""
    
    buys: List[dict]  # List of {"symbol": str, "quantity": float, "cost": float}
    sells: List[dict]  # List of {"symbol": str, "quantity": float, "proceeds": float}
    total_cost: float
    total_proceeds: float
    final_allocations: List[Allocation]
    portfolio_value: float
