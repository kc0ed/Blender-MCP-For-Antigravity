
import socket
import json
import time

HOST = "localhost"
PORT = 9876

def test_connection():
    print(f"Attempting to connect to Blender at {HOST}:{PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((HOST, PORT))
        print("✅ SUCCESS: Socket connected!")
        
        # Try to send a ping or simple command
        # Based on server.py it sends {"type": "type", "params": {}}
        command = {
            "type": "get_scene_info",
            "params": {}
        }
        print("Sending test command (get_scene_info)...")
        sock.sendall(json.dumps(command).encode('utf-8'))
        
        # Receive response
        data = sock.recv(8192)
        response = json.loads(data.decode('utf-8'))
        print(f"✅ Received response from Blender:")
        print(f"Status: {response.get('status')}")
        if 'result' in response:
             res = response['result']
             # simplify output
             print(f"Scene Name: {res.get('name', 'Unknown')}")
             print(f"Object Count: {res.get('object_count', 0)}")
        
        sock.close()
        return True
    except ConnectionRefusedError:
        print("❌ FAILED: Connection refused. Is Blender running? Is the addon enabled and 'BlenderMCP' server started in the sidebar?")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
