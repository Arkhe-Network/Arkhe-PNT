import asyncio
from playwright.async_api import async_playwright
import os
import time

async def verify_enterprise_plus():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating...")
        await page.goto("http://localhost:3000")
        await asyncio.sleep(10)

        # Click the 5th button in the tabs
        print("Clicking Wetware...")
        tabs = page.locator(".bg-arkhe-card button")
        # Let's count them or just look for the text
        wetware = page.get_by_role("button", name="WETWARE")
        await wetware.click()
        await asyncio.sleep(2)

        print("Clicking Enterprise Plus button...")
        # The button is long and specific
        btn = page.get_by_text("Arkhe(n) Enterprise Plus (25 Agents)")
        await btn.click()
        await asyncio.sleep(5)

        # Take screenshot regardless of state
        os.makedirs("/home/jules/verification", exist_ok=True)
        await page.screenshot(path="/home/jules/verification/debug_state.png", full_page=True)

        print("Done.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_enterprise_plus())
