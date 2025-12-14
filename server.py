"""
Native binary-mode Blender MCP server - Full Version
Bypasses FastMCP for Windows compatibility.
Includes all tools: Core, PolyHaven, Sketchfab, Hyper3D, Hunyuan3D
"""
import sys
import os
import json
import socket
import base64
import tempfile
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

# CRITICAL: Set binary mode FIRST on Windows
if sys.platform == 'win32':
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

# Binary stdin/stdout
stdin_bin = sys.stdin.buffer
stdout_bin = sys.stdout.buffer

def log(msg):
    sys.stderr.write(f"[BlenderMCP] {msg}\n")
    sys.stderr.flush()

# === MCP Protocol Handling ===

def read_message():
    """Read newline-delimited JSON from stdin"""
    line = b''
    while True:
        ch = stdin_bin.read(1)
        if not ch:
            return None
        if ch == b'\n':
            break
        if ch != b'\r':
            line += ch
    if not line:
        return None
    return json.loads(line.decode('utf-8'))

def write_message(msg):
    """Write JSON response with newline"""
    body = json.dumps(msg, separators=(',', ':'))
    data = body.encode('utf-8') + b'\n'
    stdout_bin.write(data)
    stdout_bin.flush()

# === Blender Connection ===

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876

@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None
    
    def connect(self) -> bool:
        if self.sock:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            log(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            log(f"Failed to connect: {e}")
            self.sock = None
            return False
    
    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
    
    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        
        command = {"type": command_type, "params": params or {}}
        self.sock.settimeout(180.0)
        self.sock.sendall(json.dumps(command).encode('utf-8'))
        
        # Receive response
        chunks = []
        while True:
            chunk = self.sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                response = json.loads(data.decode('utf-8'))
                if response.get("status") == "error":
                    raise Exception(response.get("message", "Unknown error"))
                return response.get("result", {})
            except json.JSONDecodeError:
                continue
        raise Exception("Incomplete response from Blender")

# Global connection
_connection: Optional[BlenderConnection] = None

def get_connection() -> BlenderConnection:
    global _connection
    if _connection is None:
        _connection = BlenderConnection(
            host=os.getenv("BLENDER_HOST", DEFAULT_HOST),
            port=int(os.getenv("BLENDER_PORT", DEFAULT_PORT))
        )
        if not _connection.connect():
            _connection = None
            raise Exception("Could not connect to Blender")
    return _connection

# === Tool Definitions ===

TOOLS = [
    # Core Tools
    {
        "name": "get_scene_info",
        "description": "Get detailed information about the current Blender scene",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_object_info",
        "description": "Get detailed information about a specific object in the scene",
        "inputSchema": {
            "type": "object",
            "properties": {"object_name": {"type": "string", "description": "Name of the object"}},
            "required": ["object_name"]
        }
    },
    {
        "name": "execute_blender_code",
        "description": "Execute Python code in Blender. Break complex operations into smaller steps.",
        "inputSchema": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "Python code to execute"}},
            "required": ["code"]
        }
    },
    {
        "name": "get_viewport_screenshot",
        "description": "Capture a screenshot of the current Blender 3D viewport",
        "inputSchema": {
            "type": "object",
            "properties": {"max_size": {"type": "integer", "description": "Maximum size in pixels (default 800)"}},
            "required": []
        }
    },
    
    # PolyHaven Tools
    {
        "name": "get_polyhaven_status",
        "description": "Check if PolyHaven integration is enabled in Blender",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_polyhaven_categories",
        "description": "Get categories for a specific asset type on PolyHaven",
        "inputSchema": {
            "type": "object",
            "properties": {"asset_type": {"type": "string", "description": "Asset type: hdris, textures, models, all"}},
            "required": []
        }
    },
    {
        "name": "search_polyhaven_assets",
        "description": "Search for assets on PolyHaven with optional filtering",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_type": {"type": "string", "description": "Type: hdris, textures, models, all"},
                "categories": {"type": "string", "description": "Comma-separated categories"}
            },
            "required": []
        }
    },
    {
        "name": "download_polyhaven_asset",
        "description": "Download and import a PolyHaven asset into Blender",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_id": {"type": "string", "description": "Asset ID"},
                "asset_type": {"type": "string", "description": "Type: hdris, textures, models"},
                "resolution": {"type": "string", "description": "Resolution: 1k, 2k, 4k"},
                "file_format": {"type": "string", "description": "Format: hdr, exr, jpg, png, gltf, fbx"}
            },
            "required": ["asset_id", "asset_type"]
        }
    },
    {
        "name": "set_texture",
        "description": "Apply a downloaded PolyHaven texture to an object",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Object name"},
                "texture_id": {"type": "string", "description": "PolyHaven texture ID"}
            },
            "required": ["object_name", "texture_id"]
        }
    },
    
    # Sketchfab Tools
    {
        "name": "get_sketchfab_status",
        "description": "Check if Sketchfab integration is enabled in Blender",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "search_sketchfab_models",
        "description": "Search for models on Sketchfab",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "categories": {"type": "string", "description": "Comma-separated categories"},
                "count": {"type": "integer", "description": "Max results (default 20)"},
                "downloadable": {"type": "boolean", "description": "Only downloadable models"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "download_sketchfab_model",
        "description": "Download and import a Sketchfab model by UID",
        "inputSchema": {
            "type": "object",
            "properties": {"uid": {"type": "string", "description": "Sketchfab model UID"}},
            "required": ["uid"]
        }
    },
    
    # Hyper3D Tools
    {
        "name": "get_hyper3d_status",
        "description": "Check if Hyper3D Rodin integration is enabled in Blender",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "generate_hyper3d_model_via_text",
        "description": "Generate 3D asset using Hyper3D from text description",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text_prompt": {"type": "string", "description": "Description in English"},
                "bbox_condition": {"type": "array", "items": {"type": "number"}, "description": "[Length, Width, Height] ratio"}
            },
            "required": ["text_prompt"]
        }
    },
    {
        "name": "generate_hyper3d_model_via_images",
        "description": "Generate 3D asset using Hyper3D from images",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_image_paths": {"type": "array", "items": {"type": "string"}, "description": "Absolute paths to images"},
                "input_image_urls": {"type": "array", "items": {"type": "string"}, "description": "URLs of images"},
                "bbox_condition": {"type": "array", "items": {"type": "number"}, "description": "[L,W,H] ratio"}
            },
            "required": []
        }
    },
    {
        "name": "poll_rodin_job_status",
        "description": "Check if Hyper3D Rodin generation task is completed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_key": {"type": "string", "description": "For MAIN_SITE mode"},
                "request_id": {"type": "string", "description": "For FAL_AI mode"}
            },
            "required": []
        }
    },
    {
        "name": "import_generated_asset",
        "description": "Import asset generated by Hyper3D Rodin",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Object name in scene"},
                "task_uuid": {"type": "string", "description": "For MAIN_SITE mode"},
                "request_id": {"type": "string", "description": "For FAL_AI mode"}
            },
            "required": ["name"]
        }
    },
    
    # Hunyuan3D Tools
    {
        "name": "get_hunyuan3d_status",
        "description": "Check if Hunyuan3D integration is enabled in Blender",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "generate_hunyuan3d_model",
        "description": "Generate 3D asset using Hunyuan3D from text or image",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text_prompt": {"type": "string", "description": "Text description"},
                "input_image_url": {"type": "string", "description": "Image URL"}
            },
            "required": []
        }
    },
    {
        "name": "poll_hunyuan_job_status",
        "description": "Check if Hunyuan3D generation task is completed",
        "inputSchema": {
            "type": "object",
            "properties": {"job_id": {"type": "string", "description": "Job ID from generate step"}},
            "required": ["job_id"]
        }
    },
    {
        "name": "import_generated_asset_hunyuan",
        "description": "Import asset generated by Hunyuan3D",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Object name in scene"},
                "zip_file_url": {"type": "string", "description": "ZIP file URL from generate step"}
            },
            "required": ["name", "zip_file_url"]
        }
    }
]

# === Tool Handlers ===

def _process_bbox(original_bbox):
    if original_bbox is None:
        return None
    if all(isinstance(i, int) for i in original_bbox):
        return original_bbox
    if any(i <= 0 for i in original_bbox):
        raise ValueError("bbox must be > 0")
    return [int(float(i) / max(original_bbox) * 100) for i in original_bbox]

def handle_tool_call(name: str, arguments: dict) -> str:
    try:
        conn = get_connection()
        
        # Core Tools
        if name == "get_scene_info":
            result = conn.send_command("get_scene_info")
            return json.dumps(result, indent=2)
        
        elif name == "get_object_info":
            result = conn.send_command("get_object_info", {"name": arguments.get("object_name", "")})
            return json.dumps(result, indent=2)
        
        elif name == "execute_blender_code":
            result = conn.send_command("execute_code", {"code": arguments.get("code", "")})
            return f"Code executed: {result.get('result', '')}"
        
        elif name == "get_viewport_screenshot":
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"blender_screenshot_{os.getpid()}.png")
            result = conn.send_command("get_viewport_screenshot", {
                "max_size": arguments.get("max_size", 800),
                "filepath": temp_path,
                "format": "png"
            })
            if "error" in result:
                return f"Screenshot error: {result['error']}"
            if os.path.exists(temp_path):
                with open(temp_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                os.remove(temp_path)
                return f"Screenshot captured (base64): data:image/png;base64,{img_data[:100]}..."
            return "Screenshot saved to temp file"
        
        # PolyHaven Tools
        elif name == "get_polyhaven_status":
            result = conn.send_command("get_polyhaven_status")
            return result.get("message", "PolyHaven status unknown")
        
        elif name == "get_polyhaven_categories":
            result = conn.send_command("get_polyhaven_categories", {
                "asset_type": arguments.get("asset_type", "hdris")
            })
            categories = result.get("categories", {})
            lines = [f"- {cat}: {count} assets" for cat, count in sorted(categories.items(), key=lambda x: -x[1])]
            return f"Categories:\n" + "\n".join(lines)
        
        elif name == "search_polyhaven_assets":
            result = conn.send_command("search_polyhaven_assets", {
                "asset_type": arguments.get("asset_type", "all"),
                "categories": arguments.get("categories")
            })
            assets = result.get("assets", {})
            lines = []
            for aid, data in list(assets.items())[:20]:
                lines.append(f"- {data.get('name', aid)} (ID: {aid})")
            return f"Found {result.get('total_count', 0)} assets:\n" + "\n".join(lines)
        
        elif name == "download_polyhaven_asset":
            result = conn.send_command("download_polyhaven_asset", {
                "asset_id": arguments.get("asset_id"),
                "asset_type": arguments.get("asset_type"),
                "resolution": arguments.get("resolution", "1k"),
                "file_format": arguments.get("file_format")
            })
            return result.get("message", "Asset downloaded")
        
        elif name == "set_texture":
            result = conn.send_command("set_texture", {
                "object_name": arguments.get("object_name"),
                "texture_id": arguments.get("texture_id")
            })
            return f"Texture applied: {result.get('message', 'success')}"
        
        # Sketchfab Tools
        elif name == "get_sketchfab_status":
            result = conn.send_command("get_sketchfab_status")
            return result.get("message", "Sketchfab status unknown")
        
        elif name == "search_sketchfab_models":
            result = conn.send_command("search_sketchfab_models", {
                "query": arguments.get("query", ""),
                "categories": arguments.get("categories"),
                "count": arguments.get("count", 20),
                "downloadable": arguments.get("downloadable", True)
            })
            models = result.get("results", [])
            lines = []
            for m in models[:20]:
                lines.append(f"- {m.get('name', 'Unnamed')} (UID: {m.get('uid', '?')})")
            return f"Found {len(models)} models:\n" + "\n".join(lines)
        
        elif name == "download_sketchfab_model":
            result = conn.send_command("download_sketchfab_model", {"uid": arguments.get("uid")})
            objs = result.get("imported_objects", [])
            return f"Imported: {', '.join(objs)}" if objs else "Model imported"
        
        # Hyper3D Tools
        elif name == "get_hyper3d_status":
            result = conn.send_command("get_hyper3d_status")
            return result.get("message", "Hyper3D status unknown")
        
        elif name == "generate_hyper3d_model_via_text":
            result = conn.send_command("create_rodin_job", {
                "text_prompt": arguments.get("text_prompt"),
                "images": None,
                "bbox_condition": _process_bbox(arguments.get("bbox_condition"))
            })
            if result.get("submit_time"):
                return json.dumps({"task_uuid": result["uuid"], "subscription_key": result["jobs"]["subscription_key"]})
            return json.dumps(result)
        
        elif name == "generate_hyper3d_model_via_images":
            paths = arguments.get("input_image_paths")
            urls = arguments.get("input_image_urls")
            images = None
            if paths:
                images = []
                for p in paths:
                    with open(p, "rb") as f:
                        images.append(base64.b64encode(f.read()).decode('utf-8'))
            result = conn.send_command("create_rodin_job", {
                "text_prompt": None,
                "images": images,
                "image_urls": urls,
                "bbox_condition": _process_bbox(arguments.get("bbox_condition"))
            })
            if result.get("submit_time"):
                return json.dumps({"task_uuid": result.get("uuid"), "subscription_key": result.get("jobs", {}).get("subscription_key")})
            return json.dumps(result)
        
        elif name == "poll_rodin_job_status":
            result = conn.send_command("poll_rodin_job_status", {
                "subscription_key": arguments.get("subscription_key"),
                "request_id": arguments.get("request_id")
            })
            return json.dumps(result)
        
        elif name == "import_generated_asset":
            result = conn.send_command("import_generated_asset", {
                "name": arguments.get("name"),
                "task_uuid": arguments.get("task_uuid"),
                "request_id": arguments.get("request_id")
            })
            return f"Imported: {result.get('message', 'success')}"
        
        # Hunyuan3D Tools
        elif name == "get_hunyuan3d_status":
            result = conn.send_command("get_hunyuan3d_status")
            return result.get("message", "Hunyuan3D status unknown")
        
        elif name == "generate_hunyuan3d_model":
            result = conn.send_command("generate_hunyuan3d_model", {
                "text_prompt": arguments.get("text_prompt"),
                "input_image_url": arguments.get("input_image_url")
            })
            return json.dumps(result)
        
        elif name == "poll_hunyuan_job_status":
            result = conn.send_command("poll_hunyuan_job_status", {"job_id": arguments.get("job_id")})
            return json.dumps(result)
        
        elif name == "import_generated_asset_hunyuan":
            result = conn.send_command("import_generated_asset_hunyuan", {
                "name": arguments.get("name"),
                "zip_file_url": arguments.get("zip_file_url")
            })
            return f"Imported: {result.get('message', 'success')}"
        
        else:
            return f"Unknown tool: {name}"
    
    except Exception as e:
        log(f"Tool error: {e}")
        return f"Error: {e}"

# === Main Loop ===

def main():
    log("=== Native Blender MCP Server (Full) ===")
    log(f"Tools available: {len(TOOLS)}")
    
    # Wait for initialize
    request = read_message()
    if not request or request.get('method') != 'initialize':
        log(f"Expected initialize, got: {request}")
        return
    
    log("Got initialize request")
    write_message({
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "blender-mcp-native", "version": "1.0.0"}
        }
    })
    
    # Wait for initialized notification
    notif = read_message()
    log(f"Got notification: {notif.get('method') if notif else 'None'}")
    
    # Main loop
    log("Entering main loop...")
    while True:
        msg = read_message()
        if not msg:
            log("EOF, exiting")
            break
        
        method = msg.get('method', '')
        msg_id = msg.get('id')
        params = msg.get('params', {})
        
        log(f"Method: {method}")
        
        if method == 'tools/list':
            write_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS}
            })
        
        elif method == 'tools/call':
            tool_name = params.get('name', '')
            arguments = params.get('arguments', {})
            log(f"Calling: {tool_name}")
            result_text = handle_tool_call(tool_name, arguments)
            write_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": result_text}]}
            })
        
        elif method == 'prompts/list':
            write_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"prompts": [{"name": "asset_creation_strategy", "description": "Defines the preferred strategy for creating assets in Blender"}]}
            })
        
        elif method == 'prompts/get':
            prompt_name = params.get('name', '')
            if prompt_name == 'asset_creation_strategy':
                prompt_text = """When creating 3D content in Blender, always start by checking if integrations are available:

0. Before anything, always check the scene from get_scene_info()
1. First use the following tools to verify if the following integrations are enabled:
    1. PolyHaven
        Use get_polyhaven_status() to verify its status
        If PolyHaven is enabled:
        - For objects/models: Use download_polyhaven_asset() with asset_type="models"
        - For materials/textures: Use download_polyhaven_asset() with asset_type="textures"
        - For environment lighting: Use download_polyhaven_asset() with asset_type="hdris"
    2. Sketchfab
        Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven.
        Use get_sketchfab_status() to verify its status
        If Sketchfab is enabled:
        - For objects/models: First search using search_sketchfab_models() with your query
        - Then download specific models using download_sketchfab_model() with the UID
    3. Hyper3D(Rodin)
        Hyper3D Rodin is good at generating 3D models for single item.
        Use get_hyper3d_status() to verify its status
        If Hyper3D is enabled:
        - Use generate_hyper3d_model_via_text() or generate_hyper3d_model_via_images()
        - Poll with poll_rodin_job_status()
        - Import with import_generated_asset()
    4. Hunyuan3D
        Hunyuan3D is good at generating 3D models for single item.
        Use get_hunyuan3d_status() to verify its status
        If Hunyuan3D is enabled:
        - Use generate_hunyuan3d_model()
        - Poll with poll_hunyuan_job_status()
        - Import with import_generated_asset_hunyuan()

2. Recommended asset source priority:
    - For specific existing objects: First try Sketchfab, then PolyHaven
    - For generic objects/furniture: First try PolyHaven, then Sketchfab
    - For custom or unique items: Use Hyper3D Rodin or Hunyuan3D
    - For environment lighting: Use PolyHaven HDRIs
    - For materials/textures: Use PolyHaven textures

3. Only fall back to scripting when:
    - All integrations are disabled
    - A simple primitive is explicitly requested
    - No suitable asset exists in any libraries"""
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"messages": [{"role": "assistant", "content": {"type": "text", "text": prompt_text}}]}
                })
            else:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32602, "message": f"Unknown prompt: {prompt_name}"}
                })
        
        else:
            log(f"Unknown method: {method}")
    
    # Cleanup
    if _connection:
        _connection.disconnect()
    log("=== Server Ended ===")

if __name__ == "__main__":
    main()

