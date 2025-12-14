# Windows 兼容版 Blender MCP 服务器

这是 Blender MCP 的 **Windows 兼容版本**，解决了原版在 Windows 上因 stdio 文本模式导致的协议错误问题。

## 问题背景

原版 `server.py` 使用 FastMCP 库，在 Windows 上会因为 Python 的 stdio 文本模式自动进行换行符转换（`\n` ↔ `\r\n`），导致 MCP 协议数据被破坏，出现 `invalid trailing data at the end of stream` 错误。

## 解决方案

`blender_mcp_native.py` 是一个完全重写的原生 MCP 服务器，它：

1. **使用二进制模式** - 通过 `msvcrt.setmode()` 强制 stdin/stdout 为二进制模式
2. **绕过 FastMCP** - 直接实现 MCP JSON-RPC 协议，避免库的干扰
3. **完整功能** - 包含原版所有 21 个工具和 1 个提示词

## 配置方法

在你的 MCP 客户端（如 Antigravity）配置文件中添加：

```json
{
  "mcpServers": {
    "blender": {
      "command": "C:/Users/你的用户名/AppData/Local/Programs/Python/Python312/python.exe",
      "args": [
        "D:/你的路径/blender-mcp-main/blender_mcp_native.py"
      ],
      "env": {
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

## 工具列表

### 核心工具 (4个)
- `get_scene_info` - 获取场景信息
- `get_object_info` - 获取对象信息
- `execute_blender_code` - 执行 Python 代码
- `get_viewport_screenshot` - 获取视口截图

### PolyHaven 集成 (5个)
- `get_polyhaven_status` - 检查 PolyHaven 状态
- `get_polyhaven_categories` - 获取资产分类
- `search_polyhaven_assets` - 搜索资产
- `download_polyhaven_asset` - 下载资产
- `set_texture` - 应用纹理

### Sketchfab 集成 (3个)
- `get_sketchfab_status` - 检查 Sketchfab 状态
- `search_sketchfab_models` - 搜索模型
- `download_sketchfab_model` - 下载模型

### Hyper3D Rodin 集成 (5个)
- `get_hyper3d_status` - 检查 Hyper3D 状态
- `generate_hyper3d_model_via_text` - 文本生成 3D
- `generate_hyper3d_model_via_images` - 图片生成 3D
- `poll_rodin_job_status` - 轮询任务状态
- `import_generated_asset` - 导入生成的资产

### Hunyuan3D 集成 (4个)
- `get_hunyuan3d_status` - 检查 Hunyuan3D 状态
- `generate_hunyuan3d_model` - 生成 3D 模型
- `poll_hunyuan_job_status` - 轮询任务状态
- `import_generated_asset_hunyuan` - 导入生成的资产

### 提示词 (1个)
- `asset_creation_strategy` - 资产创建策略指南

## 文件结构

```
blender-mcp-main/
├── blender_mcp_native.py    # 🔥 Windows 兼容版服务器（使用这个！）
├── addon.py                 # Blender 插件
├── src/blender_mcp/         # 原版 FastMCP 服务器（Windows 不推荐）
├── tests/                   # 调试用的测试脚本
└── debug/                   # 调试产生的临时文件
```

## 注意事项

1. 确保 Blender 正在运行并已安装 BlenderMCP 插件
2. 插件默认监听端口 `9876`
3. 如需修改端口，可设置环境变量 `BLENDER_PORT`
