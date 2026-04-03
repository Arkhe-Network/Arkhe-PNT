import asyncio
from playwright.async_api import async_playwright
import os

async def verify_enterprise_plus():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to http://localhost:3000...")
        try:
            await page.goto("http://localhost:3000", wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Initial navigation failed, trying basic goto: {e}")
            await page.goto("http://localhost:3000")

        # Wait for the dashboard header
        print("Waiting for dashboard header...")
        await page.wait_for_selector("h1:has-text('Arkhe-PNT')", timeout=30000)

        # Click on the Wetware tab (5th button in command center)
        print("Clicking Wetware tab...")
        try:
            wetware_tab = page.get_by_role("button", name="WETWARE")
            await wetware_tab.click(timeout=5000)
        except:
            print("Wetware role failed, using generic locator...")
            tabs = page.locator(".flex.gap-2.mb-4.border-b button")
            await tabs.nth(4).click()
        await asyncio.sleep(2)

        # Click on the Enterprise Plus button
        print("Clicking Enterprise Plus button...")
        try:
            enterprise_button = page.get_by_text("Arkhe(n) Enterprise Plus")
            await enterprise_button.click(timeout=5000)
        except:
            print("Enterprise text click failed, trying role...")
            await page.get_by_role("button", name="Arkhe(n) Enterprise Plus (25 Agents)").click()

        # Wait for the panel to appear
        print("Waiting for Enterprise Plus text...")
        await page.wait_for_selector("text=ARKHE(N) ENTERPRISE PLUS", timeout=10000)

        # Take a screenshot of the panel
        os.makedirs("/home/jules/verification", exist_ok=True)
        await page.screenshot(path="/home/jules/verification/enterprise_plus_panel.png")
        print("Enterprise Plus panel screenshot captured.")

        # Test Nomos G1 action
        print("Triggering Nomos G1 POC...")
        try:
            nomos_button = page.get_by_text("ACIONAR NOMOS POC")
            await nomos_button.click(timeout=5000)
        except:
            print("Action text click failed, trying locator...")
            await page.locator("button:has-text('NOMOS POC')").first.click()

        # Wait for the ZK-PROOF VERIFICADO to appear
        print("Waiting for ZK-PROOF verification...")
        await page.wait_for_selector("text=[ZK-PROOF: VERIFICADO]", timeout=15000)

        # Take a final screenshot
        await page.screenshot(path="/home/jules/verification/enterprise_plus_final.png")
        print("Final verification screenshot captured.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_enterprise_plus())
