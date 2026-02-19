@echo off
title Second Brain MCP Server
echo.
echo  ===================================
echo   SECOND BRAIN - MCP Server Startup
echo  ===================================
echo.

:: Start MCP server in background
set MCP_TRANSPORT=http
set PORT=8000
start /B python "%~dp0second_brain_mcp\server.py" >nul 2>&1
echo  [OK] MCP server starting on port 8000...
timeout /t 3 /nobreak >nul

:: Start tunnel and capture URL in temp file
set "TUNNEL_LOG=%TEMP%\second-brain-tunnel.log"
start /B "cloudflared" "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000 --protocol http2 >"%TUNNEL_LOG%" 2>&1
echo  [OK] Cloudflare tunnel starting...
timeout /t 8 /nobreak >nul

:: Extract tunnel URL
for /f "tokens=*" %%a in ('findstr "trycloudflare.com" "%TUNNEL_LOG%"') do set "TUNNEL_LINE=%%a"
for /f "tokens=4 delims=| " %%u in ("%TUNNEL_LINE%") do set "TUNNEL_URL=%%u"

echo.
echo  =============================================
echo.
echo   YOUR MCP ENDPOINT:
echo.
echo   %TUNNEL_URL%/mcp
echo.
echo  =============================================
echo.
echo   To connect Claude mobile:
echo   1. Go to claude.ai ^> Settings ^> Connectors
echo   2. Click "Add custom connector"
echo   3. Paste the URL above
echo.
echo   Press Ctrl+C to stop the server.
echo  =============================================
echo.

:: Keep window open
pause >nul
