import asyncio


async def execute_commands(page, commands: list) -> bool:
    """
    runs each command that the LLM gave us

    commands look like:
    [
        {"action": "fill", "index": 5, "value": "hello"},
        {"action": "press_enter", "index": 5}
    ]

    returns True if everything worked, False if something failed
    """

    success = True

    for cmd in commands:
        # grab the command details
        action = cmd.get("action")  # what to do: click, fill, press_enter, etc
        index = cmd.get("index")    # which element 
        value = cmd.get("value")    # value for fill/select actions

        print(f"  Executing: {action} on [{index}]" + (f" with '{value}'" if value else ""))

        try:
            # find the element using the data-idx attribute we set in get_snapshot.py
            locator = page.locator(f'[data-idx="{index}"]')

            # make sure the element actually exists before trying to do stuff
            # sometimes the page changes and elements disappear
            if index is not None and await locator.count() == 0:
                print(f"  Warning: Element [{index}] not found, skipping...")
                success = False
                continue

            # === HANDLE EACH ACTION TYPE ===

            if action == "click":
                await locator.click(timeout=5000)
                await page.wait_for_load_state("networkidle", timeout=10000)

            elif action == "fill":
                await locator.fill(value or "", timeout=5000)

            elif action == "press_enter":
                if index is not None:
                    # press enter on the specific element
                    await locator.press("Enter", timeout=5000)
                else:
                    # if no index, just press enter globally
                    await page.keyboard.press("Enter")
                # wait for page to load after submitting
                await page.wait_for_load_state("networkidle", timeout=10000)

            elif action == "select":
                await locator.select_option(value, timeout=5000)

            elif action == "scroll":
                # scroll the page up or down
                direction = value if value else "down"
                if direction == "up":
                    await page.evaluate("window.scrollBy(0, -500)")
                else:
                    await page.evaluate("window.scrollBy(0, 500)")

            elif action == "wait":
                await asyncio.sleep(int(value) if value else 2)

            # small delay between actions so we dont overwhelm the page
            # also makes it look more human like
            await asyncio.sleep(0.5)

        except Exception as e:
            # something went wrong, log it and continue
            print(f"  Error: {e}")
            success = False

    return success
