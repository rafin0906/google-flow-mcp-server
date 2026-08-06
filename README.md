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

## Direct Script Execution

Execute standard automation pipeline via `main.py`:
```bash
uv run python main.py
```


