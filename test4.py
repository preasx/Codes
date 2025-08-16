import asyncio
import random
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

URL = "https://www.profitableratecpm.com/hqx8813a?key=f56d17beb064daadfe7fb5f0fe799215"  # Chan
CLICK_LIMIT = 12  # How ma

async def click_ads():
    ua = UserAgent()
    click_count = 0

    async with async_playwright() as p:
        while click_count < CLICK_LIMIT:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=ua.random)
            page = await context.new_page()

            try:
                await page.goto(URL, timeout=60000)
                await asyncio.sleep(random.uniform(2, 5))  # Wait for page load

                # Scroll randomly
                for _ in range(random.randint(1, 3)):
                    await page.mouse.wheel(0, random.randint(200, 800))
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                # Click a random link
                links = await page.query_selector_all("a")
                if links:
                    target = random.choice(links)
                    await target.click()
                    click_count += 1
                    print(f"[+] Clicked link #{click_count}")

                await asyncio.sleep(random.uniform(2, 4))  # Wait after click

            except Exception as e:
                print(f"[!] Error: {e}")
            finally:
                await browser.close()

        print(f"✅ Done! Total clicks: {click_count}")

if __name__ == "__main__":
    asyncio.run(click_ads())