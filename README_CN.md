# Blender MCP for Antigravity (Windows 优化版)

[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Antigravity](https://img.shields.io/badge/Editor-Antigravity-purple?logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange?logo=blender&logoColor=white)](https://www.blender.org/)

**[English Documentation](README.md)**

专为 **Antigravity** 用户打造的 Blender MCP 服务器（Windows 优化版）。

此版本彻底修复了 Windows 系统下因文本模式（Text Mode）导致的 `invalid trailing data` 错误，确保 Antigravity 与 Blender 之间的连接稳定可靠。

## ✨ 核心特性

- **Windows 原生二进制模式**：绕过 Windows 默认的 `\r\n` 换行符转换问题，通信稳如老狗。
- **21+ 强力工具**：全方位控制场景、对象及第三方资产库。
- **四大集成**：开箱即支持 PolyHaven, Sketchfab, Hyper3D 和 Hunyuan3D。
- **原生极简**：基于 `server.py` 原生实现，不依赖不稳定的第三方封装库。

## 🚀 快速开始

### 1. 安装 Blender 插件
1. 打开 Blender (推荐 4.0+)。
2. 菜单栏 `Edit > Preferences > Add-ons > Install...`。
3. 选择本项目中的 `addon.py` 文件安装。
4. 勾选启用插件 ("3D Gen: Blender MCP Connect")。

### 2. 配置 Antigravity
在您的 Antigravity MCP 配置文件 (`mcp_config.json`) 中添加：

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

> **注意**: 请务必使用 Python 和 `server.py` 的**绝对路径**。

### 3. 开始使用
连接成功后，您就可以直接对 Antigravity 下令了：
- "创建一个红色的猴头"
- "去 PolyHaven 下载一个木桌模型"
- "列出场景里所有的物体"
- "检查一下 Sketchfab 能不能用"

## 🧪 关于测试

本仓库包含一个 `tests/` 文件夹，里面有一些用于自测的脚本。
- 如果遇到问题，您可以让 Antigravity "运行 tests 文件夹下的测试" 来进行自我诊断。
- `server.py` 是主程序，但 `tests/test_binary.py` 可以用来验证底层协议是否通畅。

## 📂 更多文档

更详细的开发文档（SOP、踩坑指南）已归档在本地的 `docs/` 文件夹中（为了保持仓库整洁，这些文档不会同步到 GitHub）。
