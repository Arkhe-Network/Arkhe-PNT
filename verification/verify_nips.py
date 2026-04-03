import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        print("Accessing dashboard...")
        await page.goto("http://localhost:3000")
        await asyncio.sleep(5)

        print("Clicking WETWARE tab...")
        # Use exact text from CommandCenter.tsx
        await page.click("button:has-text('Wetware')")
        await asyncio.sleep(2)

        print("Opening Enterprise Plus modal...")
        # Use exact text from CommandCenter.tsx
        await page.click("button:has-text('Arkhe(n) Enterprise Plus (25 Agents)')")
        await asyncio.sleep(3)

        # Take screenshot of the modal to verify NIP/Subnet display
        await page.screenshot(path="verification/enterprise_plus_nips.png")

        print("Checking for Subnet/NIP text...")
        content = await page.content()
        if "Subnet: NIP-01" in content:
            print("SUCCESS: Subnet/NIP mapping detected in UI")
        else:
            print("FAILURE: Subnet/NIP mapping not found")

        print("Triggering Nomos POC (G1)...")
        await page.click("button:has-text('ACIONAR NOMOS POC')")
        await asyncio.sleep(3)

        if "ZK-PROOF: VERIFICADO" in content or "VERIFICADO" in content:
             print("SUCCESS: POC action functional")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
