#!/usr/bin/env python3
"""
FastAPI app for Graphiti MCP Server with SSE transport for ChatGPT Custom Connector
"""

import os
import logging
from fastapi import FastAPI, Request

# Import the existing MCP instance
import graphiti_mcp_server
from graphiti_mcp_server import GraphitiConfig

# Set up detailed logging with environment variable debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

@app.get("/mcp/manifest.json")
def mcp_manifest():
    """MCP manifest endpoint for client discovery"""
    return {
        "id": "graphiti-memory",
        "name": "Graphiti Memory System",
        "description": "A temporally-aware knowledge graph for AI agents with episodic memory capabilities",
        "attributes": {
            "version": "1.0.0",
            "transport": "sse",
            "endpoint": "/sse",
            "capabilities": [
                "add_memory",
                "search_memory_nodes",
                "search_memory_facts",
                "delete_entity_edge",
                "delete_episode",
                "get_entity_edge",
                "get_episodes",
                "clear_graph"
            ]
        },
        "environmentVariablesJsonSchema": {
            "type": "object",
            "required": ["OPENAI_API_KEY", "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"],
            "properties": {
                "OPENAI_API_KEY": {
                    "type": "string",
                    "description": "OpenAI API key for LLM operations"
                },
                "NEO4J_URI": {
                    "type": "string",
                    "description": "Neo4j database connection URI"
                },
                "NEO4J_USER": {
                    "type": "string",
                    "description": "Neo4j database username"
                },
                "NEO4J_PASSWORD": {
                    "type": "string",
                    "description": "Neo4j database password"
                },
                "MODEL_NAME": {
                    "type": "string",
                    "description": "LLM model name (e.g., gpt-4-turbo)",
                    "default": "gpt-4-turbo"
                },
                "SMALL_MODEL_NAME": {
                    "type": "string",
                    "description": "Small LLM model for simple tasks",
                    "default": "gpt-4o-mini"
                },
                "SEMAPHORE_LIMIT": {
                    "type": "integer",
                    "description": "Concurrent operations limit",
                    "default": 10
                },
                "LLM_TEMPERATURE": {
                    "type": "number",
                    "description": "LLM temperature setting",
                    "default": 0.0
                }
            }
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize Graphiti when the app starts"""
    logger.info("Initializing Graphiti MCP Server with SSE transport for ChatGPT")
    
    # Log environment variables for debugging (without exposing sensitive values)
    logger.info("Environment variable check:")
    logger.info(f"  OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
    logger.info(f"  MODEL_NAME: {os.environ.get('MODEL_NAME', 'NOT SET')}")
    logger.info(f"  SMALL_MODEL_NAME: {os.environ.get('SMALL_MODEL_NAME', 'NOT SET')}")
    logger.info(f"  NEO4J_URI: {os.environ.get('NEO4J_URI', 'NOT SET')}")
    logger.info(f"  NEO4J_USER: {os.environ.get('NEO4J_USER', 'NOT SET')}")
    logger.info(f"  NEO4J_PASSWORD: {'SET' if os.environ.get('NEO4J_PASSWORD') else 'NOT SET'}")
    logger.info(f"  SEMAPHORE_LIMIT: {os.environ.get('SEMAPHORE_LIMIT', 'DEFAULT (10)')}")
    
    try:
        # CRITICAL: Initialize config from environment variables BEFORE calling initialize_graphiti
        logger.info("Loading configuration from environment variables...")
        graphiti_mcp_server.config = GraphitiConfig.from_env()
        logger.info("Configuration loaded successfully")
        
        # Log the loaded configuration (without sensitive values)
        logger.info(f"Config - LLM Model: {graphiti_mcp_server.config.llm.model}")
        logger.info(f"Config - Small Model: {graphiti_mcp_server.config.llm.small_model}")
        logger.info(f"Config - Temperature: {graphiti_mcp_server.config.llm.temperature}")
        logger.info(f"Config - Neo4j URI: {graphiti_mcp_server.config.neo4j.uri}")
        logger.info(f"Config - API Key Present: {bool(graphiti_mcp_server.config.llm.api_key)}")
        
        # Initialize the Graphiti server with the loaded config
        await graphiti_mcp_server.initialize_graphiti()
        logger.info("Graphiti MCP Server ready - SSE endpoint available at /sse")
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Graphiti MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)