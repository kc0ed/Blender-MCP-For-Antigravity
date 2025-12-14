"""Pure newline-delimited JSON MCP server"""
import sys
import json

def log(msg):
    print(f"[NDJSON] {msg}", file=sys.stderr, flush=True)

def read_message():
    """Read newline-delimited JSON"""
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    return json.loads(line)

def write_message(msg):
    """Write newline-delimited JSON - NO Content-Length, just JSON + newline"""
    body = json.dumps(msg, separators=(',', ':'))  # Compact JSON
    sys.stdout.write(body + "\n")
    sys.stdout.flush()
    log(f"Sent: {body[:80]}...")

log("=== NDJSON MCP Server ===")

# Initialize
log("Waiting for initialize...")
request = read_message()
log(f"Got: {json.dumps(request)[:100] if request else 'None'}")

if request and request.get('method') == 'initialize':
    write_message({
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ndjson-test", "version": "1.0.0"}
        }
    })
    
    log("Waiting for initialized...")
    notif = read_message()
    log(f"Got: {json.dumps(notif)[:100] if notif else 'None'}")
    
    log("Main loop...")
    while True:
        msg = read_message()
        if not msg:
            log("EOF")
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

log("=== Done ===")
