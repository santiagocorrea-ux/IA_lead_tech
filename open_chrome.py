from playwright.sync_api import sync_playwright

PROFILE_DIR = "/Users/10pearls/pw-debug-profile"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        PROFILE_DIR,
        channel="chrome",
        headless=False,
    )

    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://zerotrust.1ecorp.net/", wait_until="domcontentloaded")
    page.locator("#action-btn").click


    input("Press Enter to close...")
    context.close()