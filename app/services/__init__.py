# app/services/__init__.py
from app.services.project_creation import click_new_project
from app.services.clipboard_handler import copy_image_to_clipboard
from app.services.input_image_selector import (
    get_input_images,
    get_latest_image,
)
from app.services.image_pasting import (
    paste_images_into_flow,
    paste_image_into_flow,
)
from app.services.prompt_submission import (
    enter_prompt_and_send,
    enter_edit_prompt_and_send,
)
from app.services.image_download import (
    open_latest_generated_image,
    download_generated_image,
)
from app.services.screenshot_capture import take_screenshot
from app.services.ratio_selector import select_aspect_ratio
from app.services.db_handler import (
    save_project_record,
    update_project_record,
    get_latest_project_record,
)
from app.services.browser_handler import launch_flow_browser

__all__ = [
    "click_new_project",
    "copy_image_to_clipboard",
    "get_input_images",
    "get_latest_image",
    "paste_images_into_flow",
    "paste_image_into_flow",
    "enter_prompt_and_send",
    "enter_edit_prompt_and_send",
    "open_latest_generated_image",
    "download_generated_image",
    "take_screenshot",
    "select_aspect_ratio",
    "save_project_record",
    "update_project_record",
    "get_latest_project_record",
    "launch_flow_browser",
]
