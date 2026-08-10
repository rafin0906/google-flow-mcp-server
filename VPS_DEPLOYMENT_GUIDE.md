# 🚀 Google Flow MCP Server - Full Ngrok & VPS Deployment Guide

Complete step-by-step guide to run and deploy **Google Flow MCP Server** with **Ngrok** (Zero Domain Required, Free HTTPS) for 24/7 remote operation with Claude Desktop, Claude Web, Claude Mobile, and n8n.

---

## ⚡ How it Works (Single Port 8001 Architecture)

The FastMCP server on **Port 8001** serves:
1. `/mcp` -> Streamable HTTP MCP Server
2. `/downloads/*` -> Public Poster Image static route
3. `/input-images` (POST) -> HTTP endpoint for uploading reference images. Accepts raw file uploads with a required `session_id` field (an alternative to the MCP tool for external integrations, featuring identical path-traversal and extension validation).

This means **ONLY 1 NGROK TUNNEL** is needed to get full HTTPS support for both the MCP server, high-res image downloads, and image uploads!

> [!NOTE]
> `db/projects.json` now stores a `session_id` per record to ensure isolated concurrency. Legacy records created prior to this update will have `session_id: null` (this is harmless; they simply will not match any active session's "latest project" fallback lookups).

---

## 💻 1. Local Testing with Ngrok (3 Steps)

### Step 1: Start the MCP Server
Open PowerShell in `c:\MCP Servers\flow-project`:
```powershell
uv run python -m app.mcp.server http
```

### Step 2: Start Ngrok (Port 8001)
In a new terminal window:
```powershell
npx ngrok http 8001
```
*(Ngrok outputs a free HTTPS URL like: `https://xxxx-xxxx.ngrok-free.app`)*

### Step 3: Add to Claude Desktop
In Claude Desktop's **Add custom connector** modal or `claude_desktop_config.json`:
- **Remote MCP server URL:** `https://xxxx-xxxx.ngrok-free.app/mcp`
- Click **Add**!

---

## 🌐 2. Ubuntu VPS Deployment with Ngrok (24/7 Background Service)

### Prerequisites on Ubuntu VPS:
```bash
# 1. Update and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip git curl ufw

# 2. Install Playwright dependencies
sudo apt install -y libgbm1 libasound2 libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcb-dri3-0 libdrm2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm-dev

# 3. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 4. Install ngrok CLI on Ubuntu
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update && sudo apt install ngrok
```

### Authenticate Ngrok on VPS:
Get your free auth token from [dashboard.ngrok.com](https://dashboard.ngrok.com) and run:
```bash
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

---

### Systemd Services for 24/7 VPS Operation

#### Service 1: MCP Server (`/etc/systemd/system/flow-mcp.service`)
```ini
[Unit]
Description=Google Flow MCP Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/flow-project
Environment="MCP_PORT=8001"
Environment="MCP_TRANSPORT=http"
ExecStart=/root/.cargo/bin/uv run python -m app.mcp.server http
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Service 2: Ngrok Tunnel Service (`/etc/systemd/system/flow-ngrok.service`)
```ini
[Unit]
Description=Google Flow Ngrok Tunnel
After=network.target flow-mcp.service

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/ngrok http 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Start Services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now flow-mcp
sudo systemctl enable --now flow-ngrok
```

---

## 🎯 Summary

- **Local / VPS Command:** `npx ngrok http 8001`
- **Claude Desktop URL:** `https://your-ngrok-url.ngrok-free.app/mcp`
- **Status:** 100% Fully Implemented & Tested!
