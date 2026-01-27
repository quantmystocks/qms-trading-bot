"""Leaderboard API client."""

import logging
import time
from typing import List, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class LeaderboardClient:
    """Client for fetching leaderboard data."""
    
    def __init__(self, api_url: str, api_token: str, max_retries: int = 3):
        """
        Initialize leaderboard client.
        
        Args:
            api_url: Leaderboard API endpoint URL
            api_token: Authentication token
            max_retries: Maximum number of retry attempts
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        })
    
    def get_top_symbols(self, top_n: int = 5) -> List[str]:
        """
        Fetch top N symbols from leaderboard.
        
        Args:
            top_n: Number of top symbols to return (default: 5)
            
        Returns:
            List of stock symbols (strings)
            
        Raises:
            requests.RequestException: If API request fails
        """
        try:
            logger.info(f"Fetching top {top_n} symbols from leaderboard API")
            response = self.session.get(self.api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                # If response is a list of objects
                symbols = []
                for item in data[:top_n]:
                    if isinstance(item, dict):
                        # Try common field names for symbol
                        symbol = item.get("symbol") or item.get("ticker") or item.get("stock") or item.get("code")
                        if symbol:
                            symbols.append(str(symbol).upper())
                    elif isinstance(item, str):
                        symbols.append(item.upper())
            elif isinstance(data, dict):
                # If response is an object with a list field
                items = data.get("data") or data.get("results") or data.get("symbols") or data.get("stocks", [])
                symbols = []
                for item in items[:top_n]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol") or item.get("ticker") or item.get("stock") or item.get("code")
                        if symbol:
                            symbols.append(str(symbol).upper())
                    elif isinstance(item, str):
                        symbols.append(item.upper())
            else:
                raise ValueError(f"Unexpected response format: {type(data)}")
            
            if len(symbols) < top_n:
                logger.warning(f"Only received {len(symbols)} symbols, expected {top_n}")
            
            logger.info(f"Retrieved {len(symbols)} symbols: {symbols}")
            return symbols[:top_n]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching leaderboard: {e}")
            raise
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing leaderboard response: {e}")
            raise
