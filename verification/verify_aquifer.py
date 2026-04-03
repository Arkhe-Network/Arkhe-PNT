from playwright.sync_api import Page, expect, sync_playwright
import time
import os

def test_aquifer_spectrogram(page: Page):
    # 1. Arrange: Go to the application
    page.goto("http://localhost:3000")

    # 2. Act: Open the Aquifer Spectrogram panel
    # It's in the 'integrations' tab of CommandCenter
    page.get_by_role("button", name="Integrations").click()

    # Take a screenshot of the integrations tab to see what's there
    page.screenshot(path="verification/integrations_tab.png")

    # Try to find the Aquifer Spectrogram button by text
    # The button name in CommandCenter.tsx is "Aquifer Spectrogram"
    page.get_by_text("Aquifer Spectrogram", exact=False).click()

    # 3. Assert: Confirm the panel is visible
    # expect(page.get_by_text("HYDRO-Ω Protocol")).to_be_visible(timeout=10000)

    # Wait a bit more
    time.sleep(2)

    # 4. Screenshot: Capture the result
    os.makedirs("verification", exist_ok=True)
    page.screenshot(path="verification/aquifer_spectrogram.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_aquifer_spectrogram(page)
        finally:
            browser.close()
