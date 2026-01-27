"""Unit tests for leaderboard client."""

import pytest
from unittest.mock import Mock, patch
import requests
from src.leaderboard.leaderboard_client import LeaderboardClient


@patch('src.leaderboard.leaderboard_client.requests.Session')
def test_get_top_symbols_list_response(mock_session_class):
    """Test getting top symbols from list response."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {"symbol": "AAPL"},
        {"symbol": "MSFT"},
        {"symbol": "GOOGL"},
        {"symbol": "AMZN"},
        {"symbol": "TSLA"},
    ]
    mock_response.raise_for_status = Mock()
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_session.headers = {}
    mock_session_class.return_value = mock_session
    
    client = LeaderboardClient("https://api.example.com", "token123")
    symbols = client.get_top_symbols(top_n=5)
    
    assert symbols == ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    mock_session.get.assert_called_once_with("https://api.example.com", timeout=30)


@patch('src.leaderboard.leaderboard_client.requests.Session')
def test_get_top_symbols_dict_response(mock_session_class):
    """Test getting top symbols from dict response with data field."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {"symbol": "AAPL"},
            {"symbol": "MSFT"},
            {"symbol": "GOOGL"},
        ]
    }
    mock_response.raise_for_status = Mock()
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_session.headers = {}
    mock_session_class.return_value = mock_session
    
    client = LeaderboardClient("https://api.example.com", "token123")
    symbols = client.get_top_symbols(top_n=3)
    
    assert symbols == ["AAPL", "MSFT", "GOOGL"]


@patch('src.leaderboard.leaderboard_client.requests.Session')
def test_get_top_symbols_error(mock_session_class):
    """Test error handling in leaderboard client."""
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("Connection error")
    mock_session.headers = {}
    mock_session_class.return_value = mock_session
    
    client = LeaderboardClient("https://api.example.com", "token123")
    
    with pytest.raises(requests.RequestException):
        client.get_top_symbols()
