import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import DB_DIR, DB_FILE, get_public_image_url


def init_db() -> None:
    """Ensures the db directory and projects.json file exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_FILE.exists():
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"projects": []}, f, indent=2)



def load_db() -> Dict[str, Any]:
    """Loads the database content from projects.json."""
    init_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "projects" not in data:
                data = {"projects": []}
            return data
    except Exception as err:
        print(f"Error reading DB file ({DB_FILE}): {err}")
        return {"projects": []}


def save_db(data: Dict[str, Any]) -> None:
    """Saves data back to projects.json."""
    init_db()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_project_record(
    project_url: str,
    ratio: str = "4:3",
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates and stores a new project record in projects.json.
    """
    db_data = load_db()
    
    if not project_id:
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

    timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "project_id": project_id,
        "project_url": project_url,
        "ratio": ratio,
        "created_at": timestamp,
        "updated_at": timestamp,
        "image_edit_page_url": None,
        "downloaded_image_path": None,
        "public_image_url": None,
        "status": "created",
    }

    db_data["projects"].append(record)
    save_db(db_data)
    print(f"\n[DB] Project record saved successfully to {DB_FILE}:")
    print(f"     Project URL: {project_url}")
    print(f"     Ratio: {ratio}")
    return record


def update_project_record(
    project_url: Optional[str] = None,
    image_edit_page_url: Optional[str] = None,
    downloaded_image_path: Optional[str] = None,
    ratio: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Updates an existing project record matching project_url or the latest record if project_url is None.
    """
    db_data = load_db()
    projects: List[Dict[str, Any]] = db_data.get("projects", [])

    if not projects:
        print("\n[DB] No projects found in DB to update.")
        return None

    target_record: Optional[Dict[str, Any]] = None

    if project_url:
        for p in reversed(projects):
            if p.get("project_url") == project_url:
                target_record = p
                break

    if not target_record and projects:
        # Fallback to the latest record
        target_record = projects[-1]

    if not target_record:
        print(f"\n[DB] Project record matching URL '{project_url}' not found.")
        return None

    if image_edit_page_url is not None:
        target_record["image_edit_page_url"] = image_edit_page_url
    if downloaded_image_path is not None:
        target_record["downloaded_image_path"] = downloaded_image_path
        target_record["public_image_url"] = get_public_image_url(downloaded_image_path)
    if ratio is not None:
        target_record["ratio"] = ratio
    if status is not None:
        target_record["status"] = status

    target_record["updated_at"] = datetime.now(timezone.utc).isoformat()

    save_db(db_data)
    print(f"\n[DB] Project record updated successfully in {DB_FILE}:")
    print(f"     Project URL: {target_record.get('project_url')}")
    print(f"     Image Edit Page URL: {target_record.get('image_edit_page_url')}")
    print(f"     Downloaded Path: {target_record.get('downloaded_image_path')}")
    print(f"     Public Image URL: {target_record.get('public_image_url')}")
    return target_record



def get_latest_project_record() -> Optional[Dict[str, Any]]:
    """Returns the most recently created project record from projects.json."""
    db_data = load_db()
    projects = db_data.get("projects", [])
    if projects:
        return projects[-1]
    return None
