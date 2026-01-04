from playwright.async_api import async_playwright
from get_snapshot import get_page_summary
from exec_commands import execute_commands
from llm import get_llm_commands
from html_to_markdown import page_to_markdown
from extract_info import extract_info
import asyncio
import json, re


def validate_data(data: str, required_fields: list = None) -> dict:
    """
    checks if the LLM gave proper JSON
    also checks if all the fields we need are actually there
    """

    try:
        # sometimes the LLM wraps JSON in markdown code blocks like ```json ... ```
        # so we gotta strip that out first, took me a while to figure this out lol
        if "```" in data:
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', data, re.DOTALL)
            if match:
                data = match.group(1)

        # try to parse it as JSON
        parsed = json.loads(data)

        # build our result object
        result = {
            "valid": True,
            "data": parsed,
            "errors": []
        }

        # if user specified required fields
        if required_fields:
            for field in required_fields:
                if field not in parsed:
                    result["errors"].append(f"Missing field: {field}")
                    result["valid"] = False

        return result

    except json.JSONDecodeError as e:
        # JSON parsing failed, just return the raw string so we can debug
        return {
            "valid": False,
            "data": data,
            "errors": [f"Invalid JSON: {e}"]
        }


async def scrape(url: str, goal: str, required_fields: list = None, max_iterations: int = 1) -> dict:
    """
    the main scraping function - this does all the heavy lifting

    how it works:
    1. opens the url in a real browser (not headless so we can see whats happening)
    2. keeps asking the LLM what to do next until we reach the goal
    3. converts the final page to markdown
    4. asks LLM to extract the data we want
    5. validates and returns the result
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # go to the url and wait for it to fully load
        print(f"1. Opening {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle", timeout=15000)

        # this is the main loop - we keep going until LLM says we're done
        # or we hit max_iterations
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            # first, scan the page and get all clickable elements
            print("2. Analyzing page...")
            summary = await get_page_summary(page)
            print(f"   Found {summary.count('[') } elements")

            # send the page summary to LLM and ask what to do next
            print("3. Getting commands from LLM...")
            commands = get_llm_commands(summary, goal)
            print(f"   Got {len(commands)} commands: {commands}")

            # if LLM returns empty list, it means the data is already visible
            # so we can stop navigating and just extract the data
            if not commands:
                print("   No more commands needed - data should be visible")
                break

            # execute whatever the LLM told us to do (click, type, etc)
            print("4. Executing commands...")
            await execute_commands(page, commands)

            # small wait for page to stabilize after our actions
            await page.wait_for_timeout(1000)

        # now convert page to markdown for extraction
        print("\n5. Converting page to markdown...")
        markdown = await page_to_markdown(page)

        # ask LLM to pull out the specific data we wanted
        print("6. Extracting information...")
        extracted = extract_info(markdown, goal)

        # validate the result and make sure its proper JSON
        result = validate_data(extracted, required_fields)

        await browser.close()

        return result


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python scraper.py <url> <goal>")
        print('Example: python scraper.py "https://reddit.com" "get top 5 post titles"')
        sys.exit(1)

    url = sys.argv[1]
    # join all remaining args as the goal (in case they forgot quotes)
    goal = " ".join(sys.argv[2:])

    result = asyncio.run(scrape(url, goal))

    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(json.dumps(result, indent=2))

    # save to file
    with open("data.json", "w") as f:
        json.dump(result, f)
