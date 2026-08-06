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

    print("[Ratio Selector] Clicking capsule button to open ratio modal...")
    capsule_button.click()

    page.wait_for_timeout(1000)

    # 2. Wait for tablist / ratio modal to open
    print("[Ratio Selector] Waiting for ratio options tablist...")
    tablist = page.locator('div[role="tablist"]')
    tablist.wait_for(state="visible", timeout=10000)

    # 3. Locate target ratio tab
    ratio_tab = None

    # Try matching text inside role="tab" buttons
    tab_by_text = page.locator(f'div[role="tablist"] button[role="tab"]:has-text("{target_text}")')
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
        print(f"[Ratio Selector] Fallback: Searching all buttons inside tablist for '{target_text}'...")
        all_tabs = page.locator('div[role="tablist"] button')
        for i in range(all_tabs.count()):
            t = all_tabs.nth(i)
            if target_text in t.inner_text():
                ratio_tab = t
                break

    if not ratio_tab:
        raise RuntimeError(f"Could not locate aspect ratio tab for ratio '{ratio}' ({target_text})")

    print(f"[Ratio Selector] Clicking ratio tab '{target_text}'...")
    ratio_tab.click()

    page.wait_for_timeout(1500)

    print(f"[Ratio Selector] Aspect ratio '{target_text}' selected successfully.")
    return target_text
