"""Raw stdio test - NO mcp library, just pure stdin/stdout communication"""
import sys
import json
import time

# Log to stderr
def log(msg):
    print(f"[RAW] {msg}", file=sys.stderr, flush=True)

log("=== Raw Stdio Test Starting ===")
log(f"Python version: {sys.version}")
log(f"stdin encoding: {sys.stdin.encoding}")
log(f"stdout encoding: {sys.stdout.encoding}")
log(f"stdin.isatty(): {sys.stdin.isatty()}")
log(f"stdout.isatty(): {sys.stdout.isatty()}")

# Try to read from stdin
log("Attempting to read from stdin...")

try:
    # Read one line from stdin
    log("Calling sys.stdin.readline()...")
    line = sys.stdin.readline()
    log(f"Read line (length={len(line)}): {repr(line[:100] if len(line) > 100 else line)}")
    
    if not line:
        log("stdin is empty or closed (EOF)")
    else:
        # Try to parse as JSON
        try:
            data = json.loads(line)
            log(f"Parsed JSON: {json.dumps(data, indent=2)[:200]}")
            
            # Send a simple JSON-RPC response
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "serverInfo": {"name": "raw-test", "version": "1.0.0"}
                }
            }
            
            response_str = json.dumps(response)
            log(f"Sending response: {response_str[:100]}")
            
            # Write to stdout
            sys.stdout.write(response_str + "\n")
            sys.stdout.flush()
            log("Response sent!")
            
        except json.JSONDecodeError as e:
            log(f"Failed to parse JSON: {e}")
            
except Exception as e:
    log(f"Exception: {type(e).__name__}: {e}")
    import traceback
    log(traceback.format_exc())

log("=== Raw Stdio Test Ending ===")

# Keep running for a bit to see if more data comes
log("Waiting 5 seconds for more input...")
time.sleep(5)
log("Done waiting, exiting")
