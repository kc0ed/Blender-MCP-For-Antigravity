#!/usr/bin/env python3
"""Minimal MCP server for testing stdio protocol"""
import sys
import logging

# Force all logging to stderr
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
    force=True
)

from mcp.server.fastmcp import FastMCP

# Create minimal server
mcp = FastMCP("MinimalTest")

@mcp.tool()
def hello(name: str) -> str:
    """Simple hello tool for testing"""
    return f"Hello {name}!"

if __name__ == "__main__":
    mcp.run()
