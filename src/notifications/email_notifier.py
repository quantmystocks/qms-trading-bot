"""Abstract base class for email notifiers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

from ..broker.models import Allocation, TradeSummary


class EmailNotifier(ABC):
    """Abstract base class for email notification providers."""
    
    @abstractmethod
    def send_trade_summary(
        self,
        recipient: str,
        trade_summary: TradeSummary,
        leaderboard_symbols: List[str],
    ) -> bool:
        """
        Send trade summary email.
        
        Args:
            recipient: Email recipient address
            trade_summary: Trade summary data
            leaderboard_symbols: List of symbols from leaderboard
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_error_notification(
        self,
        recipient: str,
        error_message: str,
        context: Dict[str, Any] = None,
    ) -> bool:
        """
        Send error notification email.
        
        Args:
            recipient: Email recipient address
            error_message: Error message
            context: Additional context information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    def _format_trade_summary_html(
        self,
        trade_summary: TradeSummary,
        leaderboard_symbols: List[str],
    ) -> str:
        """Format trade summary as HTML email."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .summary {{ background-color: #f2f2f2; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h2>Portfolio Rebalancing Summary</h2>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h3>Leaderboard Top 5</h3>
                <p>{', '.join(leaderboard_symbols)}</p>
            </div>
        """
        
        if trade_summary.sells:
            html += """
            <h3>Stocks Sold</h3>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Proceeds</th>
                </tr>
            """
            for sell in trade_summary.sells:
                html += f"""
                <tr>
                    <td>{sell['symbol']}</td>
                    <td>{sell['quantity']:.2f}</td>
                    <td>${sell['proceeds']:.2f}</td>
                </tr>
                """
            html += "</table>"
        
        if trade_summary.buys:
            html += """
            <h3>Stocks Bought</h3>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Cost</th>
                </tr>
            """
            for buy in trade_summary.buys:
                html += f"""
                <tr>
                    <td>{buy['symbol']}</td>
                    <td>{buy['quantity']:.2f}</td>
                    <td>${buy['cost']:.2f}</td>
                </tr>
                """
            html += "</table>"
        
        html += f"""
            <div class="summary">
                <h3>Final Portfolio</h3>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Current Price</th>
                        <th>Market Value</th>
                    </tr>
        """
        
        for allocation in trade_summary.final_allocations:
            html += f"""
                    <tr>
                        <td>{allocation.symbol}</td>
                        <td>{allocation.quantity:.2f}</td>
                        <td>${allocation.current_price:.2f}</td>
                        <td>${allocation.market_value:.2f}</td>
                    </tr>
            """
        
        html += f"""
                </table>
                <p><strong>Total Portfolio Value:</strong> ${trade_summary.portfolio_value:.2f}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_trade_summary_text(
        self,
        trade_summary: TradeSummary,
        leaderboard_symbols: List[str],
    ) -> str:
        """Format trade summary as plain text email."""
        text = f"""
Portfolio Rebalancing Summary
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Leaderboard Top 5: {', '.join(leaderboard_symbols)}

"""
        
        if trade_summary.sells:
            text += "Stocks Sold:\n"
            for sell in trade_summary.sells:
                text += f"  - {sell['symbol']}: {sell['quantity']:.2f} shares, ${sell['proceeds']:.2f}\n"
            text += "\n"
        
        if trade_summary.buys:
            text += "Stocks Bought:\n"
            for buy in trade_summary.buys:
                text += f"  - {buy['symbol']}: {buy['quantity']:.2f} shares, ${buy['cost']:.2f}\n"
            text += "\n"
        
        text += "Final Portfolio:\n"
        for allocation in trade_summary.final_allocations:
            text += f"  - {allocation.symbol}: {allocation.quantity:.2f} shares @ ${allocation.current_price:.2f} = ${allocation.market_value:.2f}\n"
        
        text += f"\nTotal Portfolio Value: ${trade_summary.portfolio_value:.2f}\n"
        
        return text
