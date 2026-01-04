# AiScrapeLite

A lightweight AI-powered web scraper that uses LLMs and Playwright to intelligently navigate and extract data from websites.

## How It Works

AiScrapeLite combines browser automation with AI decision-making:

1. Opens a real browser (Chromium via Playwright)
2. Analyzes the page to identify interactive elements
3. Asks an LLM what actions to take to reach your goal
4. Executes the commands (click, fill, scroll, etc.)
5. Converts the final page to markdown
6. Uses the LLM to extract the specific data you requested
7. Returns validated JSON output

## Installation

```bash
pip install git+https://github.com/PR45H4NT/AiScrapeLite.git
```

Or for development:

```bash
git clone https://github.com/PR45H4NT/AiScrapeLite.git
cd AiScrapeLite
pip install -e .
```

After installation, install Playwright browsers:

```bash
playwright install chromium
```

## Configuration

Create a `.env` file in your project root with your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your API key from [Groq Console](https://console.groq.com/).

## Usage

### Command Line

```bash
python -m aiscrapelite.scraper "https://example.com" "extract the main heading"
```

```bash
python -m aiscrapelite.scraper "https://news.ycombinator.com" "get the top 5 post titles"
```

### Python API

```python
import asyncio
from aiscrapelite.scraper import scrape

async def main():
    result = await scrape(
        url="https://news.ycombinator.com",
        goal="get the top 5 post titles with their scores"
    )

    if result["valid"]:
        print(result["data"])
    else:
        print("Errors:", result["errors"])

asyncio.run(main())
```

### With Required Fields Validation

```python
import asyncio
from aiscrapelite.scraper import scrape

async def main():
    result = await scrape(
        url="https://github.com/trending",
        goal="get the top 3 trending repositories with name, description, and stars",
        required_fields=["name", "description", "stars"]
    )

    print(result)

asyncio.run(main())
```

### Multi-Step Navigation

For pages that require interaction before data is visible:

```python
import asyncio
from aiscrapelite.scraper import scrape

async def main():
    result = await scrape(
        url="https://reddit.com",
        goal="search for 'python' and get the first 3 post titles",
        max_iterations=3  # Allow multiple navigation steps
    )

    print(result)

asyncio.run(main())
```

## API Reference

### `scrape(url, goal, required_fields=None, max_iterations=1)`

Main scraping function.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | required | The URL to scrape |
| `goal` | `str` | required | Natural language description of what data to extract |
| `required_fields` | `list` | `None` | List of field names that must be present in the result |
| `max_iterations` | `int` | `1` | Maximum navigation steps before extracting data |

**Returns:**

```python
{
    "valid": bool,      # True if extraction succeeded and validation passed
    "data": dict/list,  # The extracted data (or raw string if parsing failed)
    "errors": list      # List of error messages (empty if valid)
}
```

## Examples

### Scrape Reddit Hot Posts

```python
result = await scrape(
    url="https://reddit.com/r/programming",
    goal="get the titles and upvote counts of the top 5 hot posts"
)
```

### Scrape Product Info

```python
result = await scrape(
    url="https://amazon.com/dp/B08N5WRWNW",
    goal="extract the product name, price, and rating",
    required_fields=["name", "price", "rating"]
)
```

### Scrape with Search

```python
result = await scrape(
    url="https://google.com",
    goal="search for 'best python libraries 2024' and get the first 3 result titles and URLs",
    max_iterations=2
)
```

## Dependencies

- `playwright` - Browser automation
- `groq` - LLM API client
- `markdownify` - HTML to markdown conversion
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## Requirements

- Python 3.10+
- Groq API key

## License

MIT
