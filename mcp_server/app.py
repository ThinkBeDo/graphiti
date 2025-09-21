#!/usr/bin/env python3
"""
FastAPI app for Graphiti MCP Server with SSE transport for ChatGPT Custom Connector
"""

import os
import logging
import argparse
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import create_fastapi_app, SSETransport

# Import the existing MCP instance and setup functions
# We need to import these carefully to avoid circular imports
import graphiti_mcp_server

# Set up logging
logger = logging.getLogger(__name__)

# Build FastAPI app with /sse endpoint for ChatGPT Custom Connector
app: FastAPI = create_fastapi_app(graphiti_mcp_server.mcp, transport_cls=SSETransport)

@app.get("/")
def root():
    """Root endpoint for health checks"""
    return {"ok": True, "service": "graphiti-mcp", "transport": "sse"}

@app.get("/healthz")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "graphiti-mcp"}

@app.on_event("startup")
async def startup_event():
    """Initialize Graphiti when the app starts"""
    logger.info("Initializing Graphiti MCP Server with SSE transport for ChatGPT")
    
    # Simulate the CLI args that the original server expects
    import sys
    sys.argv = [
        "app.py",
        "--transport", "sse",
        "--host", os.environ.get("HOST", "0.0.0.0"),
        "--port", os.environ.get("PORT", "8080")
    ]
    
    try:
        # Initialize using the existing initialization logic
        mcp_config = await graphiti_mcp_server.initialize_server()
        logger.info("Graphiti MCP Server ready - SSE endpoint available at /sse")
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Graphiti MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)