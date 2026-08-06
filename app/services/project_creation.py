# ==================================================
# PROJECT CREATION SERVICE
# ==================================================

def click_new_project(
    page,
):

    print(
        "\nWaiting for "
        "New project button..."
    )

    button = page.locator(
        "button:has-text('New project')"
    ).last

    button.wait_for(
        state="visible",
        timeout=30000,
    )

    print(
        "New project button found."
    )

    button.scroll_into_view_if_needed()

    try:

        button.click(
            timeout=15000
        )

        print(
            "New project clicked."
        )

    except Exception as error:

        print(
            "Normal click failed:"
        )

        print(
            error
        )

        print(
            "Trying JavaScript click..."
        )

        button.evaluate(
            "(element) => element.click()"
        )

        print(
            "New project clicked "
            "with JavaScript."
        )

    # Wait for project UI
    page.wait_for_timeout(
        2000
    )

    print(
        "\nCurrent URL:"
    )

    print(
        page.url
    )
