import asyncio
import sys
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Configure logging to stderr
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger("lowlevel_test")

async def run():
    server = Server("lowlevel-test")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="hello",
                description="Say hello",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
        if name == "hello":
            return [TextContent(type="text", text=f"Hello {arguments['name']}")]
        raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    
    logger.info("Starting stdio server...")
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Stdio server connected")
        await server.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(run())
