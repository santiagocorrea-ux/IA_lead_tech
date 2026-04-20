from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

PROFILE_DIR = "/Users/10pearls/pw-debug-profile"
TARGET_URL = "https://zerotrust.1ecorp.net/"
BUTTON_TEXT = "Continue as Santiago"

IFRAME_SELECTORS = [
    'iframe[src*="accounts.google.com/gsi/iframe/select"]',
    'iframe[src*="accounts.google.com/gsi"]',
    'iframe[src*="gsi/select"]',
    'iframe[title*="Sign in with Google"]',
]


def click_one_tap(page, button_text: str, overall_timeout_ms: int = 20000) -> bool:
    # Try known iframe selectors first.
    for selector in IFRAME_SELECTORS:
        try:
            page.wait_for_selector(selector, timeout=3000, state="attached")
        except PWTimeout:
            continue

        frame = page.frame_locator(selector)
        btn = frame.get_by_role("button", name=button_text)
        try:
            btn.click(timeout=overall_timeout_ms)
            return True
        except PWTimeout:
            pass

    # Fallback: scan every frame on the page for the button.
    for frame in page.frames:
        try:
            btn = frame.get_by_role("button", name=button_text)
            if btn.count() > 0:
                btn.first.click(timeout=5000)
                return True
        except Exception:
            continue

    return False


with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        PROFILE_DIR,
        channel="chrome",
        headless=False,
    )

    page = context.pages[0] if context.pages else context.new_page()
    page.goto(TARGET_URL, wait_until="domcontentloaded")

    page.locator("#action-btn").click()
    page.wait_for_timeout(1500)

    if click_one_tap(page, BUTTON_TEXT):
        print(f'Clicked "{BUTTON_TEXT}".')
    else:
        print(f'Could not find "{BUTTON_TEXT}" in any iframe.')
        print("Iframes currently on the page:")
        for f in page.frames:
            print(f"  - {f.url}")
    

    input("Press Enter to close...")
    context.close()