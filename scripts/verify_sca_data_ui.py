import asyncio
from playwright.async_api import async_playwright
import os
import time

async def verify_sca_data_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to dashboard...")
        await page.goto("http://localhost:3000")

        # Give time for the React app to initialize
        await asyncio.sleep(5)

        # Search for Arkhe-PNT in the whole page text
        print("Waiting for Arkhe-PNT text...")
        await page.wait_for_selector("text=Arkhe-PNT", timeout=30000)

        # Find and click the OPS tab button
        print("Clicking OPS tab...")
        ops_btn = page.get_by_role("button", name="OPS")
        await ops_btn.click()
        await asyncio.sleep(1)

        # Find and click the SCA-Data Coherence button
        print("Clicking SCA-Data Coherence button...")
        sca_btn = page.get_by_text("SCA-Data Coherence")
        await sca_btn.click()
        await asyncio.sleep(2)

        # Verify the modal/panel is open
        print("Verifying panel content...")
        await page.wait_for_selector("text=SCA-Data: Arkhe Data Coherence Platform", timeout=10000)

        # Take a screenshot
        os.makedirs("/home/jules/verification", exist_ok=True)
        timestamp = int(time.time())
        screenshot_path = f"/home/jules/verification/sca_data_dashboard_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")

        await browser.close()
        return screenshot_path

if __name__ == "__main__":
    try:
        path = asyncio.run(verify_sca_data_ui())
        print(f"VERIFICATION_SUCCESS:{path}")
    except Exception as e:
        print(f"VERIFICATION_FAILED: {e}")
