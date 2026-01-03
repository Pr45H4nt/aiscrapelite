async def get_page_summary(page) -> str:
    """
    scans the webpage and creates a simple list of all interactive elements
    like buttons, links, inputs etc. that the LLM can understand

    returns something like:
    [0] LINK: "Home"
    [1] INPUT: "Search"
    [2] BUTTON: "Submit"
    """

    # first, remove any data-idx attributes from previous runs
    await page.evaluate("document.querySelectorAll('[data-idx]').forEach(el => el.removeAttribute('data-idx'))")

    # this JS code runs inside the browser and scans all the elements
    summary = await page.evaluate("""
        () => {
            const lines = [];
            let visibleIdx = 0;  

            const elements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [role="searchbox"], [role="textbox"]');

            elements.forEach((el) => {
                // === SKIP HIDDEN ELEMENTS ===

                if (el.offsetParent === null && getComputedStyle(el).position !== 'fixed') return;

                if (getComputedStyle(el).visibility === 'hidden') return;
                if (getComputedStyle(el).display === 'none') return;

                const tag = el.tagName.toLowerCase();
                const role = el.getAttribute('role');

                el.setAttribute('data-idx', visibleIdx);

                // === BUILD THE DESCRIPTION FOR LLM ===

                if (tag === 'a' || role === 'link') {
                    // for links, try innerText first, then aria-label, then href
                    const text = el.innerText.trim().slice(0, 50) || el.getAttribute('aria-label') || el.href || 'link';
                    lines.push(`[${visibleIdx}] LINK: "${text}"`);
                }
                else if (tag === 'button' || role === 'button') {
                    const text = el.innerText.trim() || el.getAttribute('aria-label') || 'button';
                    lines.push(`[${visibleIdx}] BUTTON: "${text}"`);
                }
                else if (tag === 'input' || role === 'searchbox' || role === 'textbox') {
                    // for inputs, placeholder text is usually the best description
                    const placeholder = el.placeholder || el.getAttribute('aria-label') || el.name || el.type || 'input';
                    lines.push(`[${visibleIdx}] INPUT: "${placeholder}"`);
                }
                else if (tag === 'select') {
                    lines.push(`[${visibleIdx}] DROPDOWN: "${el.name || 'select'}"`);
                }
                else if (tag === 'textarea') {
                    const placeholder = el.placeholder || el.getAttribute('aria-label') || 'textarea';
                    lines.push(`[${visibleIdx}] TEXTAREA: "${placeholder}"`);
                }

                visibleIdx++; 
            });

            return lines.join('\\n');
        }
    """)

    # grab the page title and url for context
    title = await page.title()
    url = page.url

    return f"URL: {url}\nTitle: {title}\n\nElements:\n{summary}"
