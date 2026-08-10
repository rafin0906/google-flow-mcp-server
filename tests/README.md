# Google Flow MCP Server - Test Suite

This directory contains the consolidated testing scripts used to verify the isolation, stability, and session-awareness of the MCP Server.

## Prerequisites

These tests must be run from the root of the project using the initialized python environment:

```bash
uv run python tests/test_input_images_isolation.py
uv run python tests/test_project_isolation.py
```
*(Or use `.\venv\Scripts\python tests/...` if running the virtual environment directly).*

## Tests Overview

### 1. `test_input_images_isolation.py` (Tests 1-6)
Validates the `tool_input_images` flow and filesystem boundaries:
- **Test 1-4**: Basic single-session upload, text-only generation, missing session handling, and invalid inputs (path traversal defense, disallowed mime-types). Tests end-to-end `stdio_client` functionality.
- **Test 5**: Explicit two-session image upload isolation. Verifies that Session A processing correctly reads only Session A's folder, completely deletes Session A's folder afterward, and leaves Session B's folder untouched.
- **Test 6**: Crash recovery / stale session cleanup. Validates `clear_input_images()` removes left-over or orphan temporary folders perfectly.

### 2. `test_project_isolation.py` (Tests 7-9)
Validates `db/projects.json` isolation and URL resolution:
- **Test 7**: Two-session project isolation. Session A and Session B both create projects. `get_latest_project_record` and `tool_generate_poster` must fetch solely the projects matching the active session ID.
- **Test 8**: Session isolation for downstream tools. Validates that `edit_poster` and `change_ratio_and_download` fetch the correct URLs based on session ownership without crossover.
- **Test 9**: Ownership-mismatch guard. Actively simulates an attack where Session B passes Session A's explicit `project_url` to `update_project_record`. Confirms the write is safely denied and returns `None` without modifying Session A's record on disk.
