import asyncio
from playwright.async_api import async_playwright
import os
import time

async def verify_enterprise_plus():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to dashboard...")
        await page.goto("http://localhost:3000")

        # Give more time for the React app to initialize
        await asyncio.sleep(10)

        # Search for Arkhe-PNT in the whole page text
        print("Waiting for Arkhe-PNT text...")
        await page.wait_for_selector("text=Arkhe-PNT", timeout=30000)

        # Find and click the WETWARE tab button
        print("Clicking WETWARE...")
        wetware_btn = page.get_by_role("button", name="WETWARE")
        await wetware_btn.click()
        await asyncio.sleep(2)

        # Find and click the Enterprise Plus button
        print("Clicking Enterprise Plus button...")
        # Use exact text since it's unique
        enterprise_btn = page.get_by_text("Arkhe(n) Enterprise Plus (25 Agents)")
        await enterprise_btn.click()
        await asyncio.sleep(3)

        # Verify the modal/panel is open
        print("Verifying panel content...")
        await page.wait_for_selector("text=ARKHE(N) ENTERPRISE PLUS", timeout=10000)

        # Click ACIONAR NOMOS POC
        print("Triggering G1 Nomos POC...")
        nomos_poc_btn = page.get_by_text("ACIONAR NOMOS POC")
        await nomos_poc_btn.click()

        # Wait for ZK validation text
        print("Waiting for ZK-PROOF: VERIFICADO...")
        await page.wait_for_selector("text=[ZK-PROOF: VERIFICADO]", timeout=10000)

        # Take the final screenshot
        os.makedirs("/home/jules/verification", exist_ok=True)
        timestamp = int(time.time())
        screenshot_path = f"/home/jules/verification/enterprise_final_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")

        await browser.close()
        return screenshot_path

if __name__ == "__main__":
    path = asyncio.run(verify_enterprise_plus())
    print(f"VERIFICATION_SUCCESS:{path}")
