import time
from typing import Dict

# Map standard inputs to label strings and element ID suffixes
RATIO_MAP: Dict[str, Dict[str, str]] = {
    "16:9": {"text": "16:9", "trigger_id": "trigger-LANDSCAPE"},
    "16_9": {"text": "16:9", "trigger_id": "trigger-LANDSCAPE"},
    "landscape": {"text": "16:9", "trigger_id": "trigger-LANDSCAPE"},
    "4:3": {"text": "4:3", "trigger_id": "trigger-LANDSCAPE_4_3"},
    "4_3": {"text": "4:3", "trigger_id": "trigger-LANDSCAPE_4_3"},
    "landscape_4_3": {"text": "4:3", "trigger_id": "trigger-LANDSCAPE_4_3"},
    "1:1": {"text": "1:1", "trigger_id": "trigger-SQUARE"},
    "square": {"text": "1:1", "trigger_id": "trigger-SQUARE"},
    "3:4": {"text": "3:4", "trigger_id": "trigger-PORTRAIT_3_4"},
    "3_4": {"text": "3:4", "trigger_id": "trigger-PORTRAIT_3_4"},
    "portrait_3_4": {"text": "3:4", "trigger_id": "trigger-PORTRAIT_3_4"},
    "9:16": {"text": "9:16", "trigger_id": "trigger-PORTRAIT"},
    "9_16": {"text": "9:16", "trigger_id": "trigger-PORTRAIT"},
    "portrait": {"text": "9:16", "trigger_id": "trigger-PORTRAIT"},
}


def select_aspect_ratio(page, ratio: str = "4:3") -> str:
    """
    Clicks the Nano Banana 2 capsule button, opens the aspect ratio selection modal,
    and selects the requested aspect ratio.
    """
    ratio_clean = str(ratio).strip().lower()
    ratio_info = RATIO_MAP.get(ratio_clean, {"text": ratio, "trigger_id": ""})
    target_text = ratio_info["text"]
    trigger_id_suffix = ratio_info["trigger_id"]

    print(f"\n[Ratio Selector] Attempting to set aspect ratio to: {target_text} (input: '{ratio}')")

    page.wait_for_timeout(2000)

    # 1. Locate Capsule Button
    print("[Ratio Selector] Looking for Nano Banana capsule button...")

    capsule_button = None
    selectors = [
        'button:has-text("Nano Banana")',
        'button[aria-haspopup="menu"]:has-text("Banana")',
        'button:has(i:text-is("crop_landscape"))',
        'button:has(i:text-is("crop_16_9"))',
        'button:has(i:text-is("crop_square"))',
        'button:has(i:text-is("crop_portrait"))',
        'button:has(i:text-is("crop_9_16"))',
        'button[aria-haspopup="menu"]',
    ]

    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            capsule_button = loc.first
            print(f"[Ratio Selector] Found capsule button using selector: '{sel}'")
            break

    if not capsule_button:
        print("[Ratio Selector] Warning: Primary capsule selectors not immediately visible. Trying last button with menu popup...")
        capsule_button = page.locator('button[aria-haspopup="menu"]').last

    capsule_button.wait_for(state="visible", timeout=15000)
    capsule_button.scroll_into_view_if_needed()
    page.wait_for_timeout(500)

    print("[Ratio Selector] Clicking capsule button to open ratio modal...")
    try:
        capsule_button.click(timeout=5000)
        print("[Ratio Selector] Capsule button clicked via standard click.")
    except Exception as click_err:
        print(f"[Ratio Selector] Standard click failed/intercepted ({click_err}). Trying force click & JS click...")
        try:
            capsule_button.click(force=True, timeout=5000)
            print("[Ratio Selector] Capsule button clicked via force click.")
        except Exception:
            capsule_button.evaluate("(element) => element.click()")
            print("[Ratio Selector] Capsule button clicked via JavaScript evaluate.")

    page.wait_for_timeout(1000)

    # 2. Wait for ratio options container / buttons to open
    print("[Ratio Selector] Waiting for ratio options tab buttons...")
    tab_container = page.locator('div[role="tablist"]:has(button.flow_tab_slider_trigger)').first
    try:
        tab_container.wait_for(state="visible", timeout=10000)
    except Exception:
        print("[Ratio Selector] Tab container wait timed out. Re-clicking capsule button via JS...")
        capsule_button.evaluate("(element) => element.click()")
        page.wait_for_timeout(1000)
        tab_container.wait_for(state="visible", timeout=10000)

    # 3. Locate target ratio tab
    ratio_tab = None

    # Try matching text inside ratio trigger buttons
    tab_by_text = tab_container.locator(f'button:has-text("{target_text}")')
    if tab_by_text.count() > 0:
        ratio_tab = tab_by_text.first
        print(f"[Ratio Selector] Found ratio tab by text '{target_text}'")
    elif trigger_id_suffix:
        # Fallback to trigger ID
        tab_by_id = page.locator(f'button[id*="{trigger_id_suffix}"]')
        if tab_by_id.count() > 0:
            ratio_tab = tab_by_id.first
            print(f"[Ratio Selector] Found ratio tab by ID suffix '{trigger_id_suffix}'")

    if not ratio_tab or ratio_tab.count() == 0:
        print(f"[Ratio Selector] Fallback: Searching all slider trigger buttons for '{target_text}'...")
        all_tabs = page.locator('button.flow_tab_slider_trigger')
        for i in range(all_tabs.count()):
            t = all_tabs.nth(i)
            if target_text in t.inner_text():
                ratio_tab = t
                break


    if not ratio_tab:
        raise RuntimeError(f"Could not locate aspect ratio tab for ratio '{ratio}' ({target_text})")

    print(f"[Ratio Selector] Clicking ratio tab '{target_text}'...")
    try:
        ratio_tab.click(timeout=5000)
        print(f"[Ratio Selector] Ratio tab '{target_text}' clicked via standard click.")
    except Exception as tab_err:
        print(f"[Ratio Selector] Standard click on ratio tab failed ({tab_err}). Trying force click & JS click...")
        try:
            ratio_tab.click(force=True, timeout=5000)
            print(f"[Ratio Selector] Ratio tab '{target_text}' clicked via force click.")
        except Exception:
            ratio_tab.evaluate("(element) => element.click()")
            print(f"[Ratio Selector] Ratio tab '{target_text}' clicked via JavaScript evaluate.")

    page.wait_for_timeout(1000)

    # Press Escape to close any remaining radix popover container overlay
    print("[Ratio Selector] Dismissing ratio popover modal...")
    page.keyboard.press("Escape")

    page.wait_for_timeout(1000)

    print(f"[Ratio Selector] Aspect ratio '{target_text}' selected successfully.")
    return target_text

