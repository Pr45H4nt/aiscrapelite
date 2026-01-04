
from groq import Groq
from dotenv import load_dotenv
import os
import re
import json


load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def get_llm_commands(page_summary, goal, model_name="llama-3.3-70b-versatile"):
    """
    sends the page elements to the LLM and asks what to do next

    the LLM will look at all the buttons/links/inputs and decide
    which ones to click/fill to reach the goal

    returns a list of commands like:
    [{"action": "fill", "index": 5, "value": "hello"},
     {"action": "press_enter", "index": 5}]

    or empty list [] if the data is already visible on the page
    """

    # build the prompt - basically explaining to the LLM what it can do
    # and showing it the current page state
    prompt = f"""You are a browser automation assistant. \
Analyze the page and determine the NEXT step(s) to reach the goal.

PAGE:
{page_summary}

GOAL: {goal}

AVAILABLE ACTIONS:
- click: Click an element. Requires "index".
- fill: Type text into an input. Requires "index" and "value".
- press_enter: Press Enter key. Requires "index" (the input element).
- select: Choose dropdown option. Requires "index" and "value".
- scroll: Scroll the page. Optional "value": "up" or "down".
- wait: Wait for content to load.

RULES:
1. Look at the current page elements and decide what action(s) are needed NEXT.
2. For search: first "fill" the search box, then "press_enter" on same element.
3. Return 1-3 commands maximum per response.
4. If goal's data is ALREADY VISIBLE on page, return an EMPTY list: []
5. Return ONLY valid JSON - no explanation, no markdown.

EXAMPLE - Searching:
[{{"action": "fill", "index": 5, "value": "hello"}}, \
{{"action": "press_enter", "index": 5}}]

EXAMPLE - Data already visible:
[]

YOUR RESPONSE (JSON only):"""

    # call the groq API
    # temperature= 0.1 means less random/creative, more consistent outputs
    # we want the LLM to be reliable, not creative here
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a browser automation planner. "
                           "Return ONLY a JSON array of commands. "
                           "No explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    # extract the actual text response
    response = response.choices[0].message.content
    response = response.strip()

    # sometimes the LLM wraps the JSON in markdown code blocks
    # like ```json [...] ``` so we need to extract just the JSON part
    if "```" in response:
        pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            response = match.group(1)

    # try to parse as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # if parsing fails, just print what we got and return empty
        # better to do nothing than crash
        print(f"Failed to parse: {response}")
        return []


def get_llm_response(prompt, model_name="llama-3.3-70b-versatile"):
    """
    simple wrapper for getting a text response from the LLM
    used for extracting data from the final page

    just sends the prompt and returns whatever the LLM says
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1  # keep it consistent
    )

    return response.choices[0].message.content
