@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo       Blender MCP Server Launcher
echo ========================================
echo.

echo [1/3] Checking environment...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'uv' command not found!
    echo Please install 'uv' following the instructions in README.md
    echo Or run: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    pause
    exit /b 1
)
echo [OK] uv is installed.

echo [2/3] Syncing dependencies...
call uv sync
if %errorlevel% neq 0 (
    echo [ERROR] Failed to sync dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies ready.

echo [3/3] Starting Server...
echo Press Ctrl+C to stop the server.
echo.
call uv run src/blender_mcp/server.py

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Server stopped with error code %errorlevel%
)

echo.
echo Server execution finished.
pause
