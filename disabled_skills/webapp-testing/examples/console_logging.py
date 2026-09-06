from pathlib import Path

from playwright.sync_api import expect, sync_playwright

# Example: Capturing console logs during browser automation

url = 'http://localhost:5173'  # Replace with your URL

console_logs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    # Set up console log capture
    def handle_console_message(msg):
        console_logs.append(f"[{msg.type}] {msg.text}")
        print(f"Console: [{msg.type}] {msg.text}")

    page.on("console", handle_console_message)

    # Navigate to page
    page.goto(url, wait_until='domcontentloaded')
    # Replace these locators with elements observed in the target app.
    dashboard = page.get_by_role('link', name='Dashboard', exact=True)
    expect(dashboard).to_be_visible()

    # Interact with the page (triggers console logs)
    dashboard.click()
    expect(page.get_by_role('heading', name='Dashboard', exact=True)).to_be_visible()

    browser.close()

# Save console logs to file
output_dir = Path('test-artifacts')
output_dir.mkdir(exist_ok=True)
output_path = output_dir / 'console.log'
output_path.write_text('\n'.join(console_logs), encoding='utf-8')

print(f"\nCaptured {len(console_logs)} console messages")
print(f"Logs saved to: {output_path.resolve()}")
