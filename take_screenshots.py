import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("http://localhost:8501")
        
        # Wait for Streamlit to load
        await page.wait_for_selector(".stApp", state="attached", timeout=10000)
        await asyncio.sleep(2)
        
        # 1. Earth-Moon L4 Stable
        await page.click("button:has-text('Run simulation')")
        await asyncio.sleep(3)
        await page.screenshot(path="demo_fallback/l4_stable.png")
        print("Captured l4_stable.png")
        
        # 2. Earth-Moon L1 Unstable
        # Click L1 radio button
        await page.click("text='L1'")
        await asyncio.sleep(1)
        await page.click("button:has-text('Run simulation')")
        await asyncio.sleep(3)
        await page.screenshot(path="demo_fallback/l1_unstable.png")
        print("Captured l1_unstable.png")
        
        # 3. Potential Map
        # Check 'Show effective potential'
        await page.click("text='Show effective potential'")
        await asyncio.sleep(2)
        await page.screenshot(path="demo_fallback/potential_map.png")
        print("Captured potential_map.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
