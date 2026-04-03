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
        await page.click("button:has-text('Wetware')")
        await asyncio.sleep(2)

        print("Opening Enterprise Plus modal...")
        await page.click("button:has-text('Arkhe(n) Enterprise Plus (25 Agents)')")
        await asyncio.sleep(3)

        # Take screenshot of the modal to verify it opened
        await page.screenshot(path="verification/modal_opened.png")

        print("Triggering Nomos POC (G1)...")
        await page.click("button:has-text('ACIONAR NOMOS POC')")

        print("Waiting for ZK response...")
        await asyncio.sleep(5)

        # Take final screenshot
        await page.screenshot(path="verification/poc_verified.png")

        # Check text
        content = await page.content()
        if "ZK-PROOF: VERIFICADO" in content:
            print("SUCCESS: ZK-PROOF: VERIFICADO detected in UI")
        else:
            print("FAILURE: ZK-PROOF: VERIFICADO not found")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
