import argparse
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

PROFILE_DIR = "/Users/10pearls/pw-debug-profile"
TARGET_URL = "https://zerotrust.1ecorp.net/"
TASK_MANAGER_URL = "https://task-manager.1evis.net/workspaces-info"
TASK_SUMMARY = "https://task-manager.1evis.net/summary/visasgf"

BUTTON_TEXT = "Continue as Santiago"
DAYS_THRESHOLD = 2
DATE_FORMAT = "%d/%m/%Y %H:%M"

IFRAME_SELECTORS = [
    'iframe[src*="accounts.google.com/gsi/iframe/select"]',
    'iframe[src*="accounts.google.com/gsi"]',
    'iframe[src*="gsi/select"]',
    'iframe[title*="Sign in with Google"]',
]


def normalize(text: Optional[str]) -> str:
    return " ".join((text or "").split())


def click_one_tap(page, button_text: str, overall_timeout_ms: int = 20000) -> bool:
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

    for frame in page.frames:
        try:
            btn = frame.get_by_role("button", name=button_text)
            if btn.count() > 0:
                btn.first.click(timeout=5000)
                return True
        except Exception:
            continue

    return False


def wait_for_task_table(page, timeout_ms: int = 15000) -> None:
    page.goto(TASK_MANAGER_URL, wait_until="domcontentloaded")
    page.locator("table thead").wait_for(timeout=timeout_ms)
    page.locator("table tbody tr").first.wait_for(timeout=timeout_ms)

def wait_for_task_summary(page, timeout_ms: int = 15000) -> None:
    page.goto(TASK_SUMMARY, wait_until="domcontentloaded")



def extract_task_rows(page) -> List[Dict[str, Any]]:
    return page.evaluate(
        """
        () => {
            const normalize = (value) => (value || "").replace(/\\s+/g, " ").trim();

            const headers = Array.from(
                document.querySelectorAll("table thead th")
            ).map(th => normalize(th.textContent));

            const rows = Array.from(document.querySelectorAll("table tbody tr"));

            return rows.map(row => {
                const cells = Array.from(row.querySelectorAll("td"));
                const data = {};

                headers.forEach((header, index) => {
                    data[header] = normalize(cells[index]?.innerText);
                });

                const jiraDiv = row.querySelector(".jira-status");
                const actionsCell = cells[headers.indexOf("Actions")];
                const actionElements = actionsCell
                    ? Array.from(actionsCell.querySelectorAll("[title]"))
                    : [];

                const envCell = cells[headers.indexOf("Environment URL")];
                const branchCell = cells[headers.indexOf("Branch")];

                data["_meta"] = {
                    jira_id: jiraDiv?.dataset?.jiraId || null,
                    jira_status_class: normalize(jiraDiv?.className || ""),
                    environment_link: envCell?.querySelector("a")?.href || null,
                    branch_link: branchCell?.querySelector("a")?.href || null,
                    actions: actionElements.map(el => ({
                        title: el.getAttribute("title"),
                        onclick: el.getAttribute("onclick")
                    }))
                };

                return data;
            });
        }
        """
    )


def find_branch_row(rows: List[Dict[str, Any]], branch_name: str, allow_partial: bool = False) -> Optional[Dict[str, Any]]:
    target = normalize(branch_name).lower()

    exact_matches = [row for row in rows if normalize(row.get("Branch")).lower() == target]
    if exact_matches:
        return exact_matches[0]

    if allow_partial:
        partial_matches = [row for row in rows if target in normalize(row.get("Branch")).lower()]
        if len(partial_matches) == 1:
            return partial_matches[0]
        if len(partial_matches) > 1:
            matches = ", ".join(row.get("Branch", "") for row in partial_matches[:10])
            raise ValueError(f"More than one branch matched '{branch_name}': {matches}")

    return None


def get_branch_info(page, branch_name: str, timeout_ms: int = 10000, allow_partial: bool = False) -> Dict[str, Any]:
    last_match = None
    rows = []

    deadline = datetime.now().timestamp() + (timeout_ms / 1000)

    while datetime.now().timestamp() < deadline:
        rows = extract_task_rows(page)
        match = find_branch_row(rows, branch_name, allow_partial=allow_partial)

        if match:
            last_match = match
            jira_status = normalize(match.get("Jira status"))

            # Jira status is filled asynchronously, so wait until it has a value.
            if jira_status:
                break

        page.wait_for_timeout(250)

    if last_match is None:
        available = ", ".join(row.get("Branch", "") for row in rows[:15])
        raise ValueError(
            f"Branch '{branch_name}' was not found. "
            f"Some available branches: {available}"
        )

    creation_date_text = normalize(last_match.get("Creation Date"))
    creation_date = datetime.strptime(creation_date_text, DATE_FORMAT)
    now = datetime.now()
    days_since_creation = (now - creation_date).days

    return {
        **last_match,
        "Creation Date Parsed": creation_date,
        "Days Since Creation": days_since_creation,
        "Older Than Threshold": days_since_creation > DAYS_THRESHOLD,
    }


def print_branch_report(info: Dict[str, Any]) -> None:
    actions = [a["title"] for a in info["_meta"]["actions"] if a.get("title")]
    require_upgrade = "Upgrade instance" in actions
    require_downgrade = "Downgrade instance" in actions


    if require_upgrade:
        upgrade_text = "Require Upgrade enviroment"
    elif require_downgrade:
        upgrade_text = "NO Upgrade, Downgrade available"
    else:
        upgrade_text = "No"

    print("=" * 70)
    print(f"Branch:              {info.get('Branch')}")
    print(f"Environment URL:     {info.get('Environment URL')}")
    print(f"Environment status:  {info.get('Status')}")
    print(f"Creation Date:       {info.get('Creation Date')}")
    print(f"AWS Instance Type:   {info.get('AWS Instance Type')}")
    print(f"Jira status:         {info.get('Jira status') or 'Not available'}")
    print(f"Jira ID:             {info['_meta'].get('jira_id') or 'Not available'}")
    print(f"Environment link:    {info['_meta'].get('environment_link') or 'Not available'}")
    print(f"Actions:             {', '.join(actions) if actions else 'None'}")
    print()
    print("Date Comparison:")
    print
    print(upgrade_text)
    #print(f"Current Date:        {datetime.now().strftime(DATE_FORMAT)}")
    print(f"Creation Date:       {info.get('Creation Date')}")
    print(f"Days Since Creation: {info['Days Since Creation']}")
    print(f"Older than {DAYS_THRESHOLD} days? {info['Older Than Threshold']}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Look up one or more branches in the task manager."
    )
    parser.add_argument(
        "branches",
        nargs="+",
        help="One or more branch names, e.g. VISASGF-2864",
    )
    parser.add_argument(
        "--partial",
        action="store_true",
        help="Allow partial branch name matches.",
    )
    return parser.parse_args(argv)


args = parse_args()

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        PROFILE_DIR,
        channel="chrome",
        headless=False,
        no_viewport=True,
        args=["--start-maximized"],
    )

    try:
        # Zero-trust tab
        zero_page = context.pages[0] if context.pages else context.new_page()
        zero_page.goto(TARGET_URL, wait_until="domcontentloaded")
        zero_page.bring_to_front()

        # Optional login flow
        # zero_page.locator("#action-btn").click()
        # zero_page.wait_for_timeout(1500)
        # if click_one_tap(zero_page, BUTTON_TEXT):
        #     print(f'Clicked "{BUTTON_TEXT}".')
        # else:
        #     print(f'Could not find "{BUTTON_TEXT}" in any iframe.')

        task_summay = context.new_page()
        wait_for_task_summary(task_summay)

        # Open task manager in a NEW tab
        task_page = context.new_page()
        wait_for_task_table(task_page)

        # Branches from CLI args
        for branch_name in args.branches:
            try:
                info = get_branch_info(task_page, branch_name, allow_partial=args.partial)
                print_branch_report(info)
            except Exception as e:
                print("=" * 70)
                print(f"Error for branch '{branch_name}': {e}")

        input("Press Enter to close...")

    finally:
        context.close()