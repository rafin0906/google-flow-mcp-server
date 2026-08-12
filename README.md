# Google Flow Editorial Poster Scraper & MCP Server

A powerful Playwright-based automation pipeline and FastMCP server for generating, editing, and converting aspect ratios of sports/editorial graphic posters using **Google Flow** (`labs.google/fx/tools/flow`).

---

## ⚡ Server Status & Compatibility Notice

> [!IMPORTANT]
> **🟢 Local Server (Stable & Recommended)**  
> Running the server **locali (STDIO / Local HTTP)** is fully tested, stable, and works properly. Local execution provides fast response times and seamless browser session control.
>
> **🟡 Remote Server / VPS Deployment (Beta - In Development)**  
> Remote deployment via VPS / Ngrok streamable HTTP is currently in **Beta**. While operational, remote operation may experience occasional session/tunnel instability depending on network connectivity and persistent browser locks. Use with caution for production workloads.

---

## 📁 Project Directory Structure

```text
flow-project/
├── .env                       # Environment variables (PUBLIC_BASE_URL, ports, etc.)
├── .gitignore                 # Git ignore file
├── README.md                  # Project documentation & guide
├── VPS_DEPLOYMENT_GUIDE.md    # Detailed VPS systemd & Ngrok deployment guide
├── pyproject.toml             # UV / Python project dependencies configuration
├── requirements.txt           # Standard pip requirements
├── main.py                    # Direct Playwright automation execution script
├── chrome_profile/            # Persistent Chrome browser profile (Logged into Google)
├── db/                        # Local JSON database storage
│   └── projects.json          # Project session state & edit page URLs mapping
├── downloads/                 # Downloaded high-resolution output posters
├── input_images/              # Input/reference images folder (organized per session)
├── screenshots/               # Debug screenshots captured during automation steps
└── app/                       # Core application codebase
    ├── __init__.py
    ├── config.py              # Configuration, selectors, ports, and environment setup
    ├── prompts.py             # Default Google Flow prompt templates
    ├── automation/            # Low-level Playwright UI automation flow
    │   └── flow.py
    ├── boss_functions/        # High-level orchestration functions (create, generate, edit, ratio)
    │   ├── project_creator.py
    │   ├── poster_generator.py
    │   ├── poster_editor.py
    │   └── poster_ratio_editor.py
    ├── mcp/                   # FastMCP Server definition & HTTP/STDIO endpoints
    │   └── server.py
    └── services/              # Helper utilities (browser, clipboard, db, downloads, pasting)
        ├── browser_handler.py
        ├── clipboard_handler.py
        ├── db_handler.py
        ├── image_download.py
        ├── image_pasting.py
        └── prompt_submission.py
```

---

## 🛠️ Prerequisites

- **Python**: 3.10 or higher
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (Recommended) or standard `pip`
- **Browser**: Google Chrome installed on host machine
- **Google Account**: Google account logged in on Chrome (for access to `labs.google/fx/tools/flow`)

---

## 🚀 Local Setup & Installation Guide

Follow these step-by-step instructions to set up and run the project locally.

### Step 1: Clone the Repository
```bash
git clone https://github.com/rafin0906/google-flow-mcp-server.git
cd google-flow-mcp-server
```

### Step 2: Install Dependencies & Playwright
Using `uv` (Recommended):
```bash
# Create virtual environment and install dependencies
uv sync

# Install Playwright Chromium browser binaries
uv run python -m playwright install chromium
```

*Or using standard `pip`:*
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium
```

### Step 3: Create Required Folders
Ensure all essential directories exist in the project root:
```bash
# Windows PowerShell:
New-Item -ItemType Directory -Force -Path "input_images", "downloads", "screenshots", "db", "chrome_profile"

# Linux / macOS:
mkdir -p input_images downloads screenshots db chrome_profile
```

### Step 4: Environment Configuration (`.env`)
Create a `.env` file in the project root directory:
```env
PUBLIC_BASE_URL=http://localhost:8000
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
MCP_PORT=8001
MCP_TRANSPORT=stdio
```

### Step 5: Initialize Chrome Authentication Profile
To enable Google Flow automation without repeating Google logins:
1. Launch Chrome using the persistent user data directory (`chrome_profile/`).
2. Navigate to [Google Flow](https://labs.google/fx/tools/flow) and log into your Google Account.
3. Once logged in, close the browser. The session cookies will be saved in `chrome_profile/`.

---

## 🖥️ Running Locally (3 Execution Modes)

### Mode A: Direct Script Execution (`main.py`)
Run the standard Playwright poster generation pipeline directly without MCP:
```bash
# Place your reference images inside input_images/ (or subfolder)
uv run python main.py
```

### Mode B: FastMCP Server (STDIO Mode for Claude Desktop / Cursor)
Start the MCP server locally over STDIO:
```bash
uv run python -m app.mcp.server
```
or via FastMCP CLI:
```bash
uv run fastmcp run app/mcp/server.py
```

#### Connecting to Claude Desktop (Local STDIO)
Add the following snippet to your `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "google-flow": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\MCP Servers\\flow-project",
        "python",
        "-m",
        "app.mcp.server"
      ]
    }
  }
}
```

### Mode C: Interactive MCP Inspector
Test and debug MCP tools via a local web GUI:
```bash
uv run fastmcp dev inspector app/mcp/server.py
```

---

## 🌐 Remote Deployment Guide (VPS & Ngrok) [BETA]

> [!WARNING]
> Remote server mode is currently in **Beta**. You may experience occasional session locks or browser disconnects depending on network conditions.

### Step 1: Start MCP Server in HTTP Mode
On your VPS or remote machine:
```bash
uv run python -m app.mcp.server http
```
*(Server listens on port `8001` with endpoint `/mcp`)*

### Step 2: Expose via Ngrok Tunnel
In a separate terminal window, launch Ngrok on port `8001`:
```bash
npx ngrok http 8001
```
Ngrok will generate a secure HTTPS forwarding URL, e.g., `https://xxxx-xxxx.ngrok-free.app`.

### Step 3: Connect Remote Client
In Claude Desktop / MCP Client:
- **Remote Server URL**: `https://xxxx-xxxx.ngrok-free.app/mcp`

### Step 4: Web Image Uploader UI (Token-Free Uploads)
For remote users, uploading large image files as Base64 strings can consume substantial LLM context tokens. To solve this, the server provides a built-in Web Uploader UI:
- Open `https://<your-ngrok-url>/upload?session_id=<your_session_id>` in any browser.
- Drag & drop your input images.
- Images are saved directly to `input_images/<session_id>/` on the server and are automatically picked up by `tool_generate_poster`.

*For detailed 24/7 background systemd service setup on Ubuntu VPS, refer to [VPS_DEPLOYMENT_GUIDE.md](file:///c:/MCP%20Servers/flow-project/VPS_DEPLOYMENT_GUIDE.md).*

---

## 🧰 Available MCP Tools Reference

| MCP Tool Name | Description | Key Parameters |
| :--- | :--- | :--- |
| `tool_create_project` | Creates a new Google Flow canvas project and selects aspect ratio. | `ratio` ('16:9', '4:3', '1:1', '3:4', '9:16'), `session_id`, `headless` |
| `tool_get_upload_link` | Generates a Web Uploader URL for token-free image uploading. | `session_id` |
| `tool_input_images` | Saves base64 reference images directly into server's session folder. | `images_b64`, `session_id` |
| `tool_generate_poster` | Generates a poster by pasting reference images and prompt into Google Flow canvas. | `project_url`, `prompt`, `session_id`, `headless` |
| `tool_edit_poster` | Refines/edits an existing poster image with an edit prompt. | `image_edit_page_url`, `edit_prompt`, `headless` |
| `tool_poster_ratio_editor` | Changes aspect ratio of an existing generated poster image. | `edit_url`, `ratio`, `prompt`, `headless` |

---

## ⚙️ Key Configuration Settings (`app/config.py`)

- **`HEADLESS`** (default: `False`): Set to `True` for headless execution (required on headless VPS), or `False` to see browser UI steps during local execution.
- **`PUBLIC_BASE_URL`**: Used to generate public image download links when operating in remote HTTP mode.
- **`USER_DATA_DIR`**: Path to persistent Chrome user profile directory (`chrome_profile/`).

---

## 📄 License

This project is licensed under the MIT License.
