"""Raw MCP server with CORRECT Content-Length framing"""
import sys
import json

def log(msg):
    print(f"[MCP] {msg}", file=sys.stderr, flush=True)

def read_message():
    """Read a message using Content-Length framing"""
    # Read headers
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            break  # Empty line marks end of headers
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    
    # Get content length
    content_length = int(headers.get('Content-Length', 0))
    if content_length == 0:
        return None
    
    # Read body
    body = sys.stdin.read(content_length)
    return json.loads(body)

def write_message(msg):
    """Write a message using Content-Length framing"""
    body = json.dumps(msg)
    body_bytes = body.encode('utf-8')
    
    # Write header and body
    sys.stdout.write(f"Content-Length: {len(body_bytes)}\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write(body)
    sys.stdout.flush()

log("=== MCP Server with Content-Length Framing ===")

# Handle initialize
log("Waiting for initialize request...")
request = read_message()
log(f"Received: {json.dumps(request)[:100] if request else 'None'}")

if request and request.get('method') == 'initialize':
    response = {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "raw-mcp-test",
                "version": "1.0.0"
            }
        }
    }
    log(f"Sending initialize response...")
    write_message(response)
    log("Initialize response sent!")
    
    # Wait for initialized notification
    log("Waiting for initialized notification...")
    notif = read_message()
    log(f"Received: {json.dumps(notif)[:100] if notif else 'None'}")
    
    # Now handle requests in a loop
    log("Entering main loop...")
    while True:
        log("Waiting for next message...")
        msg = read_message()
        if not msg:
            log("No message received, exiting")
            break
        
        log(f"Got message: {json.dumps(msg)[:100]}")
        method = msg.get('method', '')
        msg_id = msg.get('id')
        
        if method == 'tools/list':
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "hello",
                            "description": "Say hello to someone",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Name to greet"}
                                },
                                "required": ["name"]
                            }
                        }
                    ]
                }
            }
            write_message(response)
            log("Sent tools/list response")
        elif method == 'tools/call':
            args = msg.get('params', {}).get('arguments', {})
            name = args.get('name', 'World')
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": f"Hello, {name}!"}
                    ]
                }
            }
            write_message(response)
            log(f"Sent tools/call response")
        else:
            log(f"Unknown method: {method}")

log("=== Server Ending ===")
