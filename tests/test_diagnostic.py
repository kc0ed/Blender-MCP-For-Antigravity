"""Diagnostic wrapper to capture raw stdout/stderr bytes"""
import sys
import os
import io

# Create log file to capture all output
log_path = os.path.join(os.path.dirname(__file__), "mcp_debug.log")

class StdoutCapture:
    def __init__(self, original, log_file):
        self.original = original
        self.log_file = log_file
        self.buffer = original.buffer if hasattr(original, 'buffer') else original
        
    def write(self, data):
        # Log what we're writing
        if isinstance(data, bytes):
            self.log_file.write(f"[STDOUT BYTES] {repr(data)}\n")
            self.log_file.flush()
            return self.buffer.write(data)
        else:
            self.log_file.write(f"[STDOUT TEXT] {repr(data)}\n")
            self.log_file.flush()
            return self.original.write(data)
    
    def flush(self):
        self.log_file.flush()
        if hasattr(self.original, 'flush'):
            self.original.flush()
        if hasattr(self.buffer, 'flush'):
            self.buffer.flush()
            
    def __getattr__(self, name):
        return getattr(self.original, name)

# Open log file
log_file = open(log_path, 'w', encoding='utf-8')
log_file.write("=== MCP Debug Log ===\n")
log_file.write(f"Python: {sys.version}\n")
log_file.write(f"Encoding: stdout={sys.stdout.encoding}, stderr={sys.stderr.encoding}\n")
log_file.write(f"PYTHONUTF8={os.environ.get('PYTHONUTF8', 'not set')}\n")
log_file.write("=====================\n\n")
log_file.flush()

# Wrap stdout
original_stdout = sys.stdout
sys.stdout = StdoutCapture(original_stdout, log_file)

# Now run the actual server
import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger("diagnostic")

async def run():
    server = Server("diagnostic-test")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="hello",
                description="Say hello",
                inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "hello":
            return [TextContent(type="text", text=f"Hello {arguments['name']}")]
        raise ValueError(f"Unknown tool: {name}")

    log_file.write("[INFO] Creating initialization options...\n")
    log_file.flush()
    options = server.create_initialization_options()
    
    log_file.write("[INFO] About to enter stdio_server context...\n")
    log_file.flush()
    
    async with stdio_server() as (read_stream, write_stream):
        log_file.write("[INFO] stdio_server connected, running server...\n")
        log_file.flush()
        await server.run(read_stream, write_stream, options)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        log_file.write(f"[ERROR] {type(e).__name__}: {e}\n")
        import traceback
        log_file.write(traceback.format_exc())
    finally:
        log_file.write("\n[END] Script finished\n")
        log_file.close()
