"""Webhook API for external schedulers."""

import logging
from flask import Flask, request, jsonify
from typing import Callable, Optional

logger = logging.getLogger(__name__)


def create_app(job_function: Callable, webhook_secret: Optional[str] = None) -> Flask:
    """
    Create Flask app with webhook endpoint.
    
    Args:
        job_function: Function to execute when webhook is triggered
        webhook_secret: Optional secret token for authentication
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy"}), 200
    
    @app.route("/rebalance", methods=["POST"])
    def rebalance():
        """Trigger rebalancing via webhook."""
        # Check authentication if secret is set
        if webhook_secret:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            if token != webhook_secret:
                return jsonify({"error": "Invalid authentication token"}), 401
        
        try:
            logger.info("Rebalancing triggered via webhook")
            result = job_function()
            
            return jsonify({
                "status": "success",
                "message": "Rebalancing completed",
                "trades": {
                    "buys": len(result.buys),
                    "sells": len(result.sells),
                },
            }), 200
            
        except Exception as e:
            logger.error(f"Error executing rebalancing: {e}")
            return jsonify({
                "status": "error",
                "message": str(e),
            }), 500
    
    return app
