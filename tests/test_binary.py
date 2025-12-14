"""Binary-mode MCP server - exact byte control"""
import sys
import os
import json

def log(msg):
    sys.stderr.write(f"[BIN] {msg}\n")
    sys.stderr.flush()

# Switch stdout to binary mode on Windows
if sys.platform == 'win32':
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)

# Get binary streams
stdin_bin = sys.stdin.buffer
stdout_bin = sys.stdout.buffer

def read_line():
    """Read a line from binary stdin"""
    line = b''
    while True:
        ch = stdin_bin.read(1)
        if not ch:
            return None
        if ch == b'\n':
            break
        if ch != b'\r':  # Skip carriage return
            line += ch
    return line.decode('utf-8') if line else None

def write_response(msg):
    """Write JSON response as exact bytes"""
    body = json.dumps(msg, separators=(',', ':'))
    data = body.encode('utf-8') + b'\n'
    log(f"Writing {len(data)} bytes: {data[:80]}")
    stdout_bin.write(data)
    stdout_bin.flush()

log("=== Binary MCP Server ===")

# Initialize
log("Waiting for initialize...")
line = read_line()
log(f"Got line: {line[:100] if line else 'None'}")

if line:
    request = json.loads(line)
    if request.get('method') == 'initialize':
        write_response({
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "binary-test", "version": "1.0.0"}
            }
        })
        
        log("Waiting for initialized...")
        line = read_line()
        log(f"Got: {line[:100] if line else 'None'}")
        
        log("Main loop...")
        while True:
            line = read_line()
            if not line:
                log("EOF")
                break
            
            msg = json.loads(line)
            log(f"Got: {json.dumps(msg)[:80]}")
            method = msg.get('method', '')
            msg_id = msg.get('id')
            
            if method == 'tools/list':
                write_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "hello",
                            "description": "Say hello",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                                "required": ["name"]
                            }
                        }]
                    }
                })
            elif method == 'tools/call':
                name = msg.get('params', {}).get('arguments', {}).get('name', 'World')
                write_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Hello, {name}!"}]
                    }
                })

log("=== Done ===")
