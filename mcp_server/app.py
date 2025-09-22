#!/usr/bin/env python3
"""
FastAPI app for Graphiti MCP Server with SSE transport for ChatGPT Custom Connector
"""

import os
import logging
from fastapi import FastAPI, Request

# Import the existing MCP instance
import graphiti_mcp_server

# Set up logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Graphiti MCP Server",
    description="MCP server for Graphiti memory system with SSE transport for ChatGPT",
    version="1.0.0"
)

# Add SSE endpoint for ChatGPT Custom Connector
# FastMCP provides an sse_handler method for SSE transport
@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    """Handle SSE requests from ChatGPT Custom Connector"""
    return await graphiti_mcp_server.mcp.sse_handler(request)

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
    
    try:
        # Initialize the Graphiti server
        await graphiti_mcp_server.initialize_graphiti()
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