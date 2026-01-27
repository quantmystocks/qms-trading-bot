"""Factory for creating broker instances."""

import logging
from typing import Optional

from ..config import get_config
from .broker import Broker
from .alpaca import AlpacaBroker
from .robinhood import RobinhoodBroker

logger = logging.getLogger(__name__)


def create_broker() -> Broker:
    """
    Create a broker instance based on configuration.
    
    Returns:
        Broker instance (AlpacaBroker or RobinhoodBroker)
        
    Raises:
        ValueError: If broker type is unsupported or credentials are missing
    """
    config = get_config()
    broker_type = config.broker.broker_type
    
    if broker_type == "alpaca":
        if not config.broker.alpaca_api_key or not config.broker.alpaca_api_secret:
            raise ValueError("Alpaca API key and secret are required")
        
        return AlpacaBroker(
            api_key=config.broker.alpaca_api_key,
            api_secret=config.broker.alpaca_api_secret,
            base_url=config.broker.alpaca_base_url,
        )
    
    elif broker_type == "robinhood":
        if not config.broker.robinhood_username or not config.broker.robinhood_password:
            raise ValueError("Robinhood username and password are required")
        
        return RobinhoodBroker(
            username=config.broker.robinhood_username,
            password=config.broker.robinhood_password,
            mfa_code=config.broker.robinhood_mfa_code,
        )
    
    else:
        raise ValueError(f"Unsupported broker type: {broker_type}")
