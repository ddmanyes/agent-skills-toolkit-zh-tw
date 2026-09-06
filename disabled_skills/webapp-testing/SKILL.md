---
name: webapp-testing
description: Test local web applications with Playwright to verify UI behavior, inspect rendered elements, capture screenshots, and diagnose browser logs. Use for a requested frontend check or an implementation's relevant verification.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

Use the available browser automation tool or native Python Playwright to test the local application. Follow the runtime's browser-control restrictions. Base selectors and assertions on the page or source actually inspected.

## Choose the approach

- **Static HTML:** read the file to identify relevant elements, then render and interact with it. If scripts change the content, inspect its rendered state too.
- **Existing local server:** navigate to the known URL and wait for a visible or enabled element that establishes the required view is ready.
- **Server not running:** use [with_server.py](scripts/with_server.py).
  Run it with `--help` once before first use to inspect its interface, then reuse it for single- or multiple-server lifecycle management.
  Read its source when an error, safety check, or required customization calls for it; failure is not a prerequisite for inspection.

Resolve helper paths from this Skill directory. Run the following patterns from the relevant project with the helper's absolute path substituted:

```bash
python /absolute/path/to/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

For multiple servers:

```bash
python /absolute/path/to/with_server.py   --server "cd backend && python server.py" --port 3000   --server "cd frontend && npm run dev" --port 5173   -- python your_automation.py
```

Reuse already running servers. Launch only the task's required processes and let the helper clean up the processes it starts; do not stop unrelated servers.

## Readiness and inspection

Network silence does not establish that JavaScript has completed or a particular UI is usable.
Polling or streaming may prevent `networkidle` entirely.
Wait for a concrete application state using Playwright locators/assertions with a bounded timeout.

```python
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        page = browser.new_page()
        page.goto('http://localhost:5173', wait_until='domcontentloaded')
        # Replace this with a control observed in the actual application.
        control = page.get_by_role('button', name='Save', exact=True)
        expect(control).to_be_visible()
        expect(control).to_be_enabled()
        # Inspect the view, act, then assert the observed success state.
    finally:
        browser.close()
```

Inspect the rendered DOM or screenshot, identify descriptive selectors, perform the action, and assert its visible outcome.
Locator actions provide their own actionability waits.
Use a specific response or application-state wait when the expected outcome is not visible; avoid arbitrary sleeps as evidence of completion.

## References by task

- Read [element_discovery.py](examples/element_discovery.py) when identifying buttons, links, or inputs.
- Read [static_html_automation.py](examples/static_html_automation.py) when opening local files.
- Read [console_logging.py](examples/console_logging.py) when capturing runtime messages.

Adapt example URLs, expected elements, and output paths to the inspected application. Use a writable project output directory for screenshots and logs. Capture logs only to diagnose the task and exclude secrets from shared output.

## Completion and failure

Test the requested behavior with an observable assertion.
Record the actual result, relevant screenshot or error, and checks that did not run.
Always close test-owned browsers; use headless mode unless an interactive browser is explicitly needed.

On timeout, inspect the screenshot, DOM, console, and server state before changing the wait or retrying.
Fix the identified cause within scope and repeat the failed check.
If dependencies, server access, or the browser remain unavailable, state the blocker rather than reporting a pass.
Do not write an extensive suite for a reversible visual edit when focused checks cover the behavior.
