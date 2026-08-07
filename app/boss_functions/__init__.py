# app/boss_functions/__init__.py
from typing import Any

__all__ = [
    "create_project",
    "generate_poster",
    "edit_poster",
    "change_ratio_and_download",
]

def __getattr__(name: str) -> Any:
    if name == "create_project":
        from app.boss_functions.project_creator import create_project
        return create_project
    elif name == "generate_poster":
        from app.boss_functions.poster_generator import generate_poster
        return generate_poster
    elif name == "edit_poster":
        from app.boss_functions.poster_editor import edit_poster
        return edit_poster
    elif name == "change_ratio_and_download":
        from app.boss_functions.poster_ratio_editor import change_ratio_and_download
        return change_ratio_and_download
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

