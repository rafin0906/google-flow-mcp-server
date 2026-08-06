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

    textbox.scroll_into_view_if_needed()

    textbox.click(
        timeout=15000,
    )

    page.wait_for_timeout(
        1000
    )

    # ==========================================
    # COPY PROMPT TO CLIPBOARD
    # ==========================================

    print(
        "\nCopying complete prompt "
        "to clipboard..."
    )

    pyperclip.copy(
        target_prompt
    )


    # ==========================================
    # PASTE PROMPT ONCE
    # ==========================================

    print(
        "Pasting complete prompt "
        "into Flow..."
    )

    textbox.press(
        "Control+V"
    )

    # Give Slate editor time
    page.wait_for_timeout(
        3000
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

        if PROMPT_END_MARKER in target_prompt:
            if PROMPT_END_MARKER in current_text:
                prompt_complete = True
                break
        else:
            if len(current_text) > 0:
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
