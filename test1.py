import asyncio
import random
import base64
import requests
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

# ----------------- CONFIG -----------------
URL = "https://gapcontroversialprodigal.com/qqn3dsg1k?key=1c7efe0549f34497bcd9d2e5edc1f5c6"  # Ad/Test URL
CLICK_LIMIT = 12  # How many ad clicks before stopping

# ----------------- SCATTERED GIST URL PARTS -----------------
PART_A = "aHR0cHM6Ly9naXN0Lmdp"
PART_B = "dGh1YnVzZXJjb250ZW50LmNvbS9E"
PART_C = "dGVjaDJwcmVhcy84MWJmMmI1"
PART_D = "OTU3YzFjYTQ2Njg3YTYwNzRmMjNmOTI3MC9yYXcvbmFtZXMudHh0"

def reconstruct_gist_url():
    """Combine scattered base64 parts and decode to get real gist URL"""
    combined = PART_A + PART_B + PART_C + PART_D
    return base64.b64decode(combined).decode()
# -------------------------------------------------------------

def get_valid_urls():
    """Fetch valid ad URLs from the gist, only if gist URL matches expected."""
    gist_url = reconstruct_gist_url()
    try:
        resp = requests.get(gist_url, timeout=10)
        if resp.status_code == 200:
            # Normalize lines: strip whitespace and trailing slashes
            return [line.strip().rstrip("/") for line in resp.text.splitlines() if line.strip()]
    except Exception as e:
        print(f"[!] Could not fetch gist: {e}")
    return []

async def click_ads():
    ua = UserAgent()
    click_count = 0

    # ✅ Validate URL against gist list
    valid_urls = get_valid_urls()
    normalized_url = URL.strip().rstrip("/")
    if normalized_url not in valid_urls:
        print("[!] Current ad URL is not in the approved gist list. Script aborted.")
        return

    print(f"[+] Ad URL validated against gist. Starting with {URL}")

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