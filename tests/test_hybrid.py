"""Hybrid MCP server - reads newline JSON, responds with Content-Length"""
import sys
import json

def log(msg):
    print(f"[HYBRID] {msg}", file=sys.stderr, flush=True)

def read_message():
    """Read newline-delimited JSON message"""
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    return json.loads(line)

def write_message(msg):
    """Write with Content-Length framing"""
    body = json.dumps(msg)
    body_bytes = body.encode('utf-8')
    sys.stdout.write(f"Content-Length: {len(body_bytes)}\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write(body)
    sys.stdout.flush()
    log(f"Sent: {body[:80]}...")

log("=== Hybrid MCP Server ===")

# Handle initialize
log("Waiting for initialize...")
request = read_message()
log(f"Got: {json.dumps(request)[:100] if request else 'None'}")

if request and request.get('method') == 'initialize':
    response = {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "hybrid-test", "version": "1.0.0"}
        }
    }
    write_message(response)
    
    # Wait for initialized notification
    log("Waiting for initialized...")
    notif = read_message()
    log(f"Got: {json.dumps(notif)[:100] if notif else 'None'}")
    
    # Main loop
    log("Entering main loop...")
    while True:
        msg = read_message()
        if not msg:
            log("EOF, exiting")
            break
        
        log(f"Got: {json.dumps(msg)[:80]}")
        method = msg.get('method', '')
        msg_id = msg.get('id')
        
        if method == 'tools/list':
            write_message({
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
            write_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": f"Hello, {name}!"}]
                }
            })
        else:
            log(f"Unknown: {method}")

log("=== Server Ending ===")
