from playwright.sync_api import Page, expect, sync_playwright
import time

def test_velxio_panel(page: Page):
    # 1. Navigate to the dashboard
    page.goto("http://localhost:5173")

    # Wait for the application to load
    page.wait_for_selector("text=Command Center")

    # 2. Open the Integrations tab
    integrations_tab = page.get_by_role("button", name="Integrations")
    integrations_tab.click()

    # 3. Click the Velxio HIL Bridge button
    velxio_button = page.get_by_text("Velxio HIL Bridge")
    velxio_button.click()

    # 4. Verify the panel is visible
    expect(page.get_by_text("Velxio // Hardware Emulation Bridge")).to_be_visible()

    # 5. Take a screenshot of the initial setup
    page.screenshot(path="verification/velxio_setup.png")

    # 6. Start simulation
    run_button = page.get_by_role("button", name="Run HIL Simulation")
    run_button.click()

    # Wait for simulation to complete (it has several steps with 800ms-1200ms delays)
    # Total wait time should be around 5-7 seconds
    time.sleep(8)

    # 7. Take a screenshot of the result
    page.screenshot(path="verification/velxio_result.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Set viewport size to capture the full modal
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        try:
            test_velxio_panel(page)
        except Exception as e:
            print(f"Error during verification: {e}")
            # Take a screenshot on error
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
