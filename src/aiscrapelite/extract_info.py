from llm import get_llm_response


def extract_info(markdown: str, goal: str) -> str:
    """
    sends the page content (as markdown) to the LLM and asks it
    to extract whatever the user wanted

    for example if goal is "get top 5 posts", the LLM will look through
    the markdown and pull out the post titles

    returns JSON string with the extracted data
    """

    # build a simple prompt asking the LLM to extract the data
    # we limit to 6000 chars cuz LLMs have token limits and
    # the important stuff is usually at the top anyway
    prompt = f"""Extract the requested information from this page.

GOAL: {goal}

PAGE CONTENT:
{markdown[:6000]}

Return the extracted data as JSON. Only include what's actually on the page."""

    # let the LLM do its magic
    return get_llm_response(prompt)
