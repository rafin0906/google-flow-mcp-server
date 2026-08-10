# Google Flow Editorial Poster Scraper & Automation

A Playwright-based automation pipeline for generating sports editorial graphic posters using Google Flow.

## Project Architecture

```
newlab/
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                   # Primary entry point
├── flow_scraper.py           # Legacy entry point wrapper
└── app/
    ├── __init__.py
    ├── config.py             # Configs, selectors, and directory paths
    ├── prompts.py            # FLOW_PROMPT text templates
    ├── utils/
    │   ├── __init__.py
    │   ├── clipboard.py      # Windows clipboard image copy helper
    │   └── image.py          # Directory image scanning logic
    └── automation/
        ├── __init__.py
        └── flow.py           # Playwright UI steps & automation pipeline
```

## Prerequisites

- Python 3.10+
- Google Chrome browser
- Pre-configured `chrome_profile/` directory logged into Google

## Setup & Execution with UV

This project is configured to use [`uv`](https://github.com/astral-sh/uv) for fast, isolated Python package and environment management.

### 1. Initialize / Install Dependencies
```bash
uv sync
uv run python -m playwright install chromium
```

### 2. Run FastMCP Server
To run the FastMCP server via STDIO (for Claude Desktop, Cursor, or MCP clients):
```bash
uv run python -m app.mcp.server
```
or using FastMCP CLI:
```bash
uv run fastmcp run app/mcp/server.py
```

### 3. Run MCP Inspector Mode
To launch the MCP Server with interactive web-based Inspector:
```bash
uv run fastmcp dev inspector app/mcp/server.py
```
or via npx:
```bash
npx @modelcontextprotocol/inspector uv run python -m app.mcp.server
```

### 4. Connect with Claude Desktop

Add the following block to your `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-flow": {
      "command": "C:/Users/sohel/AppData/Roaming/Python/Python312/Scripts/uv.exe",
      "args": [
        "--directory",
        "c:/MCP Servers/flow-project",
        "run",
        "python",
        "-m",
        "app.mcp.server"
      ]
    }
  }
}
```

---

## Usage & Workflow (Session Isolation)

The MCP server is fully session-aware, allowing multiple concurrent users or conversations to generate and edit projects in isolation.

- **Strict Session Requirement**: Every tool call (`tool_create_project`, `tool_input_images`, `tool_generate_poster`, `tool_edit_poster`, `tool_poster_ratio_editor`) requires an active MCP session context. This is handled automatically for normal MCP client connections. If session context is missing, the tool will raise a clear error.
- **Reference Images**: If you want to use reference images, call `tool_input_images` FIRST. It securely uploads images to a session-isolated folder on the server. `tool_generate_poster` will then automatically pick them up; there is no need to pass `images_b64` directly to it anymore (though it is still accepted as an optional override).
- **Per-Session Project State**: Project state (`project_url`, `image_edit_page_url`, etc.) is tracked per-session in `db/projects.json`. Each tool's "use the latest project" fallback (when explicit URLs aren't passed) strictly targets the CALLING SESSION'S own projects. Concurrent users can safely use the server simultaneously without their projects, edits, or uploaded images interfering.
- **Queueing Behavior**: Image generation runs one at a time (not in parallel) due to the shared Chromium browser profile. Concurrent requests are safely queued, not dropped.

---

## Direct Script Execution

Execute standard automation pipeline via `main.py`:
```bash
uv run python main.py
```


