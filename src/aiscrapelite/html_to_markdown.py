import re
from markdownify import markdownify as md


async def page_to_markdown(page) -> str:
    """
    takes the current page HTML and converts it to markdown
    """

    # get the full HTML of the page
    html = await page.content()

    # === CLEAN UP THE HTML ===
    # remove stuff that just adds noise and confuses the LLM

    flags = re.DOTALL | re.IGNORECASE

    # remove all <script> tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=flags)

    # remove all <style> tags - CSS doesnt matter for content extraction
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=flags)

    # remove navigation
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=flags)

    # remove footer
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=flags)

    # convert to markdown using the markdownify library
    markdown = md(html, heading_style="ATX")

    # clean up excessive newlines (more than 2 in a row)
    # makes the output way more readable
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown.strip()
