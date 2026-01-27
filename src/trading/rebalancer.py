"""Portfolio rebalancing logic."""

import logging
from typing import List, Optional
from ..broker import Broker
from ..broker.models import Allocation, TradeSummary
from ..leaderboard import LeaderboardClient
from ..notifications import EmailNotifier

logger = logging.getLogger(__name__)


class Rebalancer:
    """Handles portfolio rebalancing based on leaderboard rankings."""
    
    def __init__(
        self,
        broker: Broker,
        leaderboard_client: LeaderboardClient,
        initial_capital: float,
        email_notifier: Optional[EmailNotifier] = None,
    ):
        """
        Initialize rebalancer.
        
        Args:
            broker: Broker instance
            leaderboard_client: Leaderboard API client
            initial_capital: Initial capital for portfolio allocation
            email_notifier: Optional email notifier
        """
        self.broker = broker
        self.leaderboard_client = leaderboard_client
        self.initial_capital = initial_capital
        self.email_notifier = email_notifier
    
    def rebalance(self) -> TradeSummary:
        """
        Execute portfolio rebalancing.
        
        Returns:
            TradeSummary with details of executed trades
        """
        logger.info("Starting portfolio rebalancing")
        
        # Fetch leaderboard top 5
        try:
            leaderboard_symbols = self.leaderboard_client.get_top_symbols(top_n=5)
            logger.info(f"Leaderboard top 5: {leaderboard_symbols}")
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            raise
        
        # Get current allocation
        try:
            current_allocations = self.broker.get_current_allocation()
            current_symbols = {alloc.symbol.upper() for alloc in current_allocations}
            logger.info(f"Current positions: {current_symbols}")
        except Exception as e:
            logger.error(f"Error getting current allocation: {e}")
            raise
        
        # Normalize leaderboard symbols to uppercase
        leaderboard_symbols_upper = [s.upper() for s in leaderboard_symbols]
        
        # Check if rebalancing is needed
        if not current_allocations:
            # No current allocation - initial setup
            logger.info("No current positions found. Performing initial allocation")
            return self._initial_allocation(leaderboard_symbols_upper)
        
        # Check if current allocation matches leaderboard
        if self._allocations_match(current_allocations, leaderboard_symbols_upper):
            logger.info("Current allocation matches leaderboard. No rebalancing needed.")
            # Still create a summary for email
            return self._create_summary([], [], current_allocations)
        
        # Rebalancing needed
        logger.info("Rebalancing needed. Executing trades...")
        return self._execute_rebalancing(current_allocations, leaderboard_symbols_upper)
    
    def _allocations_match(self, allocations: List[Allocation], target_symbols: List[str]) -> bool:
        """Check if current allocations match target symbols."""
        current_symbols = {alloc.symbol.upper() for alloc in allocations}
        target_set = {s.upper() for s in target_symbols}
        
        # Check if we have exactly the top 5 symbols
        return current_symbols == target_set and len(current_symbols) == 5
    
    def _initial_allocation(self, symbols: List[str]) -> TradeSummary:
        """Perform initial allocation when portfolio is empty."""
        buys = []
        allocation_per_stock = self.initial_capital / len(symbols)
        
        logger.info(f"Dividing ${self.initial_capital} into {len(symbols)} stocks: ${allocation_per_stock} each")
        
        for symbol in symbols:
            try:
                success = self.broker.buy(symbol, allocation_per_stock)
                if success:
                    buys.append({
                        "symbol": symbol,
                        "quantity": 0,  # Will be updated after getting positions
                        "cost": allocation_per_stock,
                    })
                    logger.info(f"Bought ${allocation_per_stock} of {symbol}")
                else:
                    logger.warning(f"Failed to buy {symbol}")
            except Exception as e:
                logger.error(f"Error buying {symbol}: {e}")
        
        # Get updated allocations
        try:
            final_allocations = self.broker.get_current_allocation()
            # Update quantities in buys
            for buy in buys:
                for alloc in final_allocations:
                    if alloc.symbol.upper() == buy["symbol"].upper():
                        buy["quantity"] = alloc.quantity
                        break
        except Exception as e:
            logger.error(f"Error getting final allocations: {e}")
            final_allocations = []
        
        return self._create_summary(buys, [], final_allocations)
    
    def _execute_rebalancing(
        self,
        current_allocations: List[Allocation],
        target_symbols: List[str],
    ) -> TradeSummary:
        """Execute rebalancing trades."""
        current_symbols = {alloc.symbol.upper() for alloc in current_allocations}
        target_set = {s.upper() for s in target_symbols}
        
        # Find symbols to sell (not in top 5)
        symbols_to_sell = current_symbols - target_set
        
        # Find symbols to buy (in top 5 but not currently held)
        symbols_to_buy = target_set - current_symbols
        
        sells = []
        buys = []
        
        # Sell positions not in top 5
        total_proceeds = 0.0
        for symbol in symbols_to_sell:
            allocation = next((a for a in current_allocations if a.symbol.upper() == symbol), None)
            if allocation:
                try:
                    success = self.broker.sell(symbol, allocation.quantity)
                    if success:
                        sells.append({
                            "symbol": symbol,
                            "quantity": allocation.quantity,
                            "proceeds": allocation.market_value,
                        })
                        total_proceeds += allocation.market_value
                        logger.info(f"Sold {allocation.quantity} shares of {symbol} for ${allocation.market_value}")
                    else:
                        logger.warning(f"Failed to sell {symbol}")
                except Exception as e:
                    logger.error(f"Error selling {symbol}: {e}")
        
        # Get available cash (from sales + existing cash)
        try:
            available_cash = self.broker.get_account_cash()
            logger.info(f"Available cash: ${available_cash}")
        except Exception as e:
            logger.error(f"Error getting account cash: {e}")
            available_cash = total_proceeds
        
        # Buy missing positions (equal weight)
        if symbols_to_buy:
            allocation_per_stock = available_cash / len(symbols_to_buy)
            logger.info(f"Buying {len(symbols_to_buy)} stocks with ${allocation_per_stock} each")
            
            for symbol in symbols_to_buy:
                try:
                    success = self.broker.buy(symbol, allocation_per_stock)
                    if success:
                        buys.append({
                            "symbol": symbol,
                            "quantity": 0,  # Will be updated
                            "cost": allocation_per_stock,
                        })
                        logger.info(f"Bought ${allocation_per_stock} of {symbol}")
                    else:
                        logger.warning(f"Failed to buy {symbol}")
                except Exception as e:
                    logger.error(f"Error buying {symbol}: {e}")
        
        # Get final allocations
        try:
            final_allocations = self.broker.get_current_allocation()
            # Update quantities in buys
            for buy in buys:
                for alloc in final_allocations:
                    if alloc.symbol.upper() == buy["symbol"].upper():
                        buy["quantity"] = alloc.quantity
                        break
        except Exception as e:
            logger.error(f"Error getting final allocations: {e}")
            final_allocations = []
        
        return self._create_summary(buys, sells, final_allocations)
    
    def _create_summary(
        self,
        buys: List[dict],
        sells: List[dict],
        final_allocations: List[Allocation],
    ) -> TradeSummary:
        """Create trade summary."""
        total_cost = sum(buy.get("cost", 0) for buy in buys)
        total_proceeds = sum(sell.get("proceeds", 0) for sell in sells)
        portfolio_value = sum(alloc.market_value for alloc in final_allocations)
        
        summary = TradeSummary(
            buys=buys,
            sells=sells,
            total_cost=total_cost,
            total_proceeds=total_proceeds,
            final_allocations=final_allocations,
            portfolio_value=portfolio_value,
        )
        
        # Note: Email notification is handled in main.py after rebalancing completes
        # to have access to config for recipient address
        
        return summary
