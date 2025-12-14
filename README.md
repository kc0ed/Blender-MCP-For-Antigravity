# Blender MCP for Antigravity (Windows Optimized)

[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Antigravity](https://img.shields.io/badge/Editor-Antigravity-purple?logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange?logo=blender&logoColor=white)](https://www.blender.org/)

**[中文文档 (Chinese Documentation)](README_CN.md)**

A robust, **Windows-optimized** Model Context Protocol (MCP) server for Blender, specifically designed for **Antigravity** users.

This fork fixes the critical "invalid trailing data" error caused by Windows stdio text mode handling, ensuring a stable connection between Antigravity and Blender.

## ✨ Key Features

- **Windows Native Binary Mode**: Completely bypasses Windows text-mode `\r\n` issues.
- **21+ Tools**: Full control over scene, objects, and external assets.
- **Integrations**: Built-in support for PolyHaven, Sketchfab, Hyper3D, and Hunyuan3D.
- **Stable**: Custom-built server (`server.py`) independent of unstable libraries.

## 🚀 Quick Start

### 1. Install Blender Addon
1. Open Blender (4.0+ recommended).
2. Go to `Edit > Preferences > Add-ons > Install...`.
3. Select `addon.py` from this repository.
4. Enable the add-on ("3D Gen: Blender MCP Connect").

### 2. Configure Antigravity
Add the following to your Antigravity MCP configuration (`mcp_config.json`):

```json
{
  "mcpServers": {
    "blender": {
      "command": "C:/Path/To/Your/python.exe",
      "args": [
        "D:/Path/To/This/Repo/server.py"
      ],
      "env": {
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

> **Note**: Make sure to use the absolute path to your Python executable and the `server.py` file.

### 3. Usage
Once connected, you can ask Antigravity to:
- "Create a red monkey head"
- "Download a wooden table from PolyHaven"
- "List all objects in the scene"
- "Check if Sketchfab integration is working"

## 🧪 Testing

This repository includes a `tests/` folder with scripts to verify functionality.
- You can ask Antigravity to "Run the tests in the tests folder" to self-diagnose issues.
- `server.py` is the main entry point, but `tests/test_binary.py` can verify low-level protocol health.

## 📂 Documentation

Advanced documentation (SOPs, Troubleshooting Guides) is available in the local `docs/` folder (not uploaded to GitHub to keep the repo clean).
