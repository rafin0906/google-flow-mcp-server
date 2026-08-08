import time
import pyperclip

from app.config import (
    TEXTBOX_SELECTOR,
    SEND_BUTTON_SELECTOR,
    PROMPT_END_MARKER,
)
from app.prompts import FLOW_PROMPT


# ==================================================
# PROMPT SUBMISSION SERVICE
# ==================================================

JS_PASTE_TEXT = """
([element, text]) => {
    const target = element || document.querySelector("div[role='textbox'][contenteditable='true']") || document.activeElement;
    if (target && target.focus) {
        target.focus();
    }
    const dataTransfer = new DataTransfer();
    dataTransfer.setData("text/plain", text);
    const event = new ClipboardEvent("paste", {
        clipboardData: dataTransfer,
        bubbles: true,
        cancelable: true
    });
    if (target) {
        target.dispatchEvent(event);
    }
    const slateEditor = document.querySelector("div[role='textbox'][contenteditable='true']");
    if (slateEditor && slateEditor !== target) {
        slateEditor.dispatchEvent(event);
    }
    return true;
}
"""


def is_user_prompt_present(text_box_content: str, target_prompt: str) -> bool:
    """Checks if actual user prompt text is present in the Slate editor, ignoring placeholder text."""
    clean_text = text_box_content.replace("What do you want to create?", "").strip()
    if not clean_text:
        return False
    if PROMPT_END_MARKER in target_prompt:
        return PROMPT_END_MARKER in clean_text
    return len(clean_text) > 0


def insert_text_into_flow(page, textbox, text: str):
    print(f"\n[insert_text_into_flow] Inserting prompt ({len(text)} chars)...")
    textbox.scroll_into_view_if_needed()
    try:
        textbox.click(timeout=5000)
    except Exception:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        textbox.click(timeout=5000, force=True)

    textbox.focus()
    page.wait_for_timeout(500)

    # 1. Clear any existing content
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.wait_for_timeout(300)

    # 2. Insert text via Playwright CDP keyboard insert_text (triggers Slate.js beforeinput event)
    print("[insert_text_into_flow] Typing text via page.keyboard.insert_text...")
    page.keyboard.insert_text(text)
    page.wait_for_timeout(1000)

    current_text = textbox.inner_text().strip()

    # 3. Fallback: Try pyperclip + Control+V if insert_text didn't populate
    if not is_user_prompt_present(current_text, text):
        print("[insert_text_into_flow] Text not populated, trying pyperclip + Control+V fallback...")
        try:
            pyperclip.copy(text)
            textbox.focus()
            page.keyboard.press("Control+V")
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"[insert_text_into_flow] pyperclip error: {e}")
        current_text = textbox.inner_text().strip()

    # 4. Fallback: Try JS DataTransfer paste event if still not present
    if not is_user_prompt_present(current_text, text):
        print("[insert_text_into_flow] Trying JS DataTransfer paste event fallback...")
        try:
            page.evaluate(JS_PASTE_TEXT, [textbox.element_handle(), text])
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"[insert_text_into_flow] JS paste error: {e}")

    # 5. Trigger React input update
    page.keyboard.press("Space")
    page.wait_for_timeout(200)
    page.keyboard.press("Backspace")
    page.wait_for_timeout(500)


def enter_prompt_and_send(
    page,
    prompt_text=None,
):

    target_prompt = prompt_text if prompt_text is not None else FLOW_PROMPT

    print(
        "\nWaiting for Flow textbox..."
    )

    textbox = page.locator(
        TEXTBOX_SELECTOR
    ).last

    textbox.wait_for(
        state="visible",
        timeout=30000,
    )

    print(
        "Inserting prompt into Flow..."
    )

    insert_text_into_flow(page, textbox, target_prompt)

    # Give Slate editor time
    page.wait_for_timeout(
        2000
    )

    # ==========================================
    # WAIT FOR END MARKER
    # ==========================================

    print(
        "Waiting for the full prompt "
        "to appear..."
    )

    prompt_timeout_ms = 30000

    start_time = time.monotonic()

    prompt_complete = False

    while True:

        current_text = (
            textbox.inner_text()
            .strip()
        )

        if is_user_prompt_present(current_text, target_prompt):
            prompt_complete = True
            break


        elapsed_ms = (
            time.monotonic()
            - start_time
        ) * 1000

        if (
            elapsed_ms
            >= prompt_timeout_ms
        ):

            break

        page.wait_for_timeout(
            1000
        )

    # ==========================================
    # BLOCK SEND IF PROMPT IS INCOMPLETE
    # ==========================================

    if not prompt_complete:

        current_text = (
            textbox.inner_text()
            .strip()
        )

        print(
            "\nPROMPT VERIFICATION FAILED"
        )

        print(
            "Current textbox length:",
            len(current_text),
        )

        print(
            "Expected prompt length:",
            len(FLOW_PROMPT),
        )

        raise RuntimeError(
            "The full prompt did not "
            "appear in Flow.\n"
            "Send button was NOT clicked."
        )

    print(
        "\nFull prompt verified."
    )

    print(
        "Textbox length:",
        len(current_text),
    )

    # ==========================================
    # WAIT FOR UI TO STABILIZE
    # ==========================================

    print(
        "Waiting 5 seconds for "
        "Flow UI to stabilize..."
    )

    page.wait_for_timeout(
        5000
    )

    # ==========================================
    # FIND SEND BUTTON
    # ==========================================

    print(
        "Waiting for Send button..."
    )

    send_button = page.locator(
        SEND_BUTTON_SELECTOR
    ).last

    send_button.wait_for(
        state="visible",
        timeout=30000,
    )

    # ==========================================
    # WAIT UNTIL ENABLED
    # ==========================================

    send_timeout_ms = 30000

    start_time = time.monotonic()

    send_enabled = False

    while True:

        aria_disabled = (
            send_button.get_attribute(
                "aria-disabled"
            )
        )

        if (
            aria_disabled
            != "true"
        ):

            send_enabled = True

            break

        elapsed_ms = (
            time.monotonic()
            - start_time
        ) * 1000

        if (
            elapsed_ms
            >= send_timeout_ms
        ):

            break

        page.wait_for_timeout(
            500
        )

    if not send_enabled:

        raise RuntimeError(
            "Send button remained "
            "disabled for 60 seconds.\n"
            "Nothing was sent."
        )

    print(
        "Send button is enabled."
    )

    # ==========================================
    # FINAL CHECK
    # ==========================================

    final_text = (
        textbox.inner_text()
        .strip()
    )

    if PROMPT_END_MARKER in target_prompt and PROMPT_END_MARKER not in final_text:
        raise RuntimeError(
            "FINAL SAFETY STOP:\n"
            "Prompt end marker disappeared.\n"
            "Nothing was sent."
        )


    print(
        "Final prompt verification "
        "passed."
    )

    # ==========================================
    # CLICK ONLY ONCE (WITH ROBUST FALLBACKS)
    # ==========================================

    print(
        "\nClicking Send button..."
    )

    try:
        send_button.click(
            timeout=5000,
            no_wait_after=True,
        )
        print("Send clicked via standard click.")
    except Exception as click_err:
        print(f"Standard click on Send button timed out or failed ({click_err}).")
        print("Attempting force click and JS evaluate fallbacks...")
        try:
            send_button.click(
                force=True,
                timeout=5000,
                no_wait_after=True,
            )
            print("Send clicked via force click.")
        except Exception:
            send_button.evaluate("(element) => element.click()")
            print("Send clicked via JavaScript evaluate.")

    print(
        "Send click completed."
    )


    # ==========================================
    # PREVENT ANY SECOND CLICK
    # ==========================================

    page.wait_for_timeout(
        3000
    )

    print(
        "Submission finished."
    )

    # ==========================================
    # WAIT FOR NEW IMAGE GENERATION (60s)
    # ==========================================

    print(
        "\nWaiting 60 seconds for Flow to "
        "generate the new image..."
    )

    page.wait_for_timeout(
        60_000
    )

    print(
        "60-second generation wait completed."
    )


# ==================================================
# EDIT PROMPT SUBMISSION SERVICE (FAST IMMEDIATE CLICK)
# ==================================================

def enter_edit_prompt_and_send(
    page,
    prompt_text,
):
    """
    Submits prompt on the image edit page and immediately clicks Send
    without waiting for disabled state checks or long stabilization delays.
    """
    print("\nWaiting for Flow textbox on edit page...")
    textbox = page.locator(TEXTBOX_SELECTOR).last
    textbox.wait_for(state="visible", timeout=30000)
    textbox.scroll_into_view_if_needed()

    try:
        textbox.click(timeout=3000)
    except Exception:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        textbox.click(timeout=5000, force=True)

    page.wait_for_timeout(1000)

    print("Inserting editing prompt into Flow...")
    insert_text_into_flow(page, textbox, prompt_text)
    page.wait_for_timeout(1000)

    print("\nLocating Send button on edit page...")
    send_selectors = [
        SEND_BUTTON_SELECTOR,
        "button:has(i:text-is('arrow_forward'))",
        "button:has(i:text-is('send'))",
        "button:has(i:has-text('arrow_forward'))",
        "button[type='submit']",
    ]

    send_button = None
    for sel in send_selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.last.is_visible():
            send_button = loc.last
            break

    if not send_button:
        send_button = page.locator(SEND_BUTTON_SELECTOR).last

    print("Clicking Send button immediately (no wait)...")
    try:
        send_button.click(timeout=3000, no_wait_after=True)
        print("Send clicked via standard click.")
    except Exception as click_err:
        print(f"Standard click on Send button failed ({click_err}). Attempting force/JS click...")
        try:
            send_button.click(force=True, timeout=3000, no_wait_after=True)
            print("Send clicked via force click.")
        except Exception:
            send_button.evaluate("(element) => element.click()")
            print("Send clicked via JavaScript evaluate.")

    page.wait_for_timeout(3000)

    print("\nWaiting 40 seconds for Flow to generate the new edited image variation...")
    page.wait_for_timeout(40_000)
    print("40-second generation wait completed.")


