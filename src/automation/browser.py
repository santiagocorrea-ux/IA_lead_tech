"""Playwright browser automation for the task manager dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from playwright.sync_api import TimeoutError as PWTimeout

from src import config


# ---------------------------------------------------------------------------
# Selectors for Google One-Tap login iframe
# ---------------------------------------------------------------------------
_IFRAME_SELECTORS = [
    'iframe[src*="accounts.google.com/gsi/iframe/select"]',
    'iframe[src*="accounts.google.com/gsi"]',
    'iframe[src*="gsi/select"]',
    'iframe[title*="Sign in with Google"]',
]


def normalize(text: str | None) -> str:
    return " ".join((text or "").split())


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def navigate_to_task_table(page: Any, timeout_ms: int = 15000) -> None:
    page.goto(config.TASK_MANAGER_URL, wait_until="domcontentloaded")
    page.locator("table thead").wait_for(timeout=timeout_ms)
    page.locator("table tbody tr").first.wait_for(timeout=timeout_ms)


def navigate_to_task_summary(page: Any) -> None:
    page.goto(config.TASK_SUMMARY_URL, wait_until="domcontentloaded")


# ---------------------------------------------------------------------------
# Google One-Tap
# ---------------------------------------------------------------------------

def click_one_tap(page: Any, button_text: str = config.GOOGLE_BUTTON_TEXT, timeout_ms: int = 20000) -> bool:
    """Attempt to click the Google One-Tap button. Returns True if clicked."""
    for selector in _IFRAME_SELECTORS:
        try:
            page.wait_for_selector(selector, timeout=3000, state="attached")
        except PWTimeout:
            continue
        frame = page.frame_locator(selector)
        btn = frame.get_by_role("button", name=button_text)
        try:
            btn.click(timeout=timeout_ms)
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


# ---------------------------------------------------------------------------
# DOM scraping
# ---------------------------------------------------------------------------

def extract_task_rows(page: Any) -> list[dict[str, Any]]:
    """Evaluate JavaScript on the task table and return row data."""
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


def find_branch_row(
    rows: list[dict[str, Any]],
    branch_name: str,
    allow_partial: bool = False,
) -> dict[str, Any] | None:
    target = normalize(branch_name).lower()

    exact = [r for r in rows if normalize(r.get("Branch")).lower() == target]
    if exact:
        return exact[0]

    if allow_partial:
        partial = [r for r in rows if target in normalize(r.get("Branch")).lower()]
        if len(partial) == 1:
            return partial[0]
        if len(partial) > 1:
            matches = ", ".join(r.get("Branch", "") for r in partial[:10])
            raise ValueError(f"More than one branch matched '{branch_name}': {matches}")

    return None


def get_branch_info(
    page: Any,
    branch_name: str,
    timeout_ms: int = 10000,
    allow_partial: bool = False,
) -> dict[str, Any]:
    """
    Poll the task table until a row for branch_name is found with a Jira status.
    Raises ValueError if the branch is not found within timeout_ms.
    """
    last_match: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    deadline = datetime.now().timestamp() + (timeout_ms / 1000)

    while datetime.now().timestamp() < deadline:
        rows = extract_task_rows(page)
        match = find_branch_row(rows, branch_name, allow_partial=allow_partial)

        if match:
            last_match = match
            if normalize(match.get("Jira status")):
                break

        page.wait_for_timeout(250)

    if last_match is None:
        available = ", ".join(r.get("Branch", "") for r in rows[:15])
        raise ValueError(
            f"Branch '{branch_name}' was not found. Available branches: {available}"
        )

    creation_date = datetime.strptime(normalize(last_match.get("Creation Date")), config.DATE_FORMAT)
    days_old = (datetime.now() - creation_date).days

    return {
        **last_match,
        "Creation Date Parsed": creation_date,
        "Days Since Creation": days_old,
        "Older Than Threshold": days_old > config.DAYS_THRESHOLD,
    }
