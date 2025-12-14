"""Keep-alive MCP server - stays running and logs everything"""
import sys
import os
import asyncio
import logging
import time

# Redirect all logging to stderr immediately
logging.basicConfig(
    level=logging.DEBUG, 
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger("keepalive")

# Log startup info
logger.info("=== Keep-Alive MCP Server Starting ===")
logger.info(f"Python: {sys.version}")
logger.info(f"stdin encoding: {sys.stdin.encoding}")
logger.info(f"stdout encoding: {sys.stdout.encoding}")
logger.info(f"stdin isatty: {sys.stdin.isatty()}")
logger.info(f"stdout isatty: {sys.stdout.isatty()}")

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

async def run():
    server = Server("keepalive-test")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        logger.info("list_tools called!")
        return [
            Tool(
                name="hello",
                description="Say hello",
                inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        logger.info(f"call_tool called: {name} with {arguments}")
        if name == "hello":
            return [TextContent(type="text", text=f"Hello {arguments['name']}")]
        raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    logger.info("Initialization options created")
    
    logger.info("Entering stdio_server context...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio_server context entered successfully")
            logger.info(f"read_stream type: {type(read_stream)}")
            logger.info(f"write_stream type: {type(write_stream)}")
            
            logger.info("Calling server.run()...")
            await server.run(read_stream, write_stream, options)
            logger.info("server.run() returned normally")
    except Exception as e:
        logger.error(f"Exception in stdio_server: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("Exiting run() function")

if __name__ == "__main__":
    logger.info("Starting asyncio.run()")
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Top-level exception: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
    logger.info("Script ending")
