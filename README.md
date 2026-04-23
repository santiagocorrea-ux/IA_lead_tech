# IAproject

AI-assisted toolkit for the VISASGF board. Three workflows:

1. **Test case generation** — Jira story → JSON → VISA-formatted Excel
2. **Branch health check** — Task manager dashboard + Bitbucket commit metrics
3. **Form automation** — JavaScript injection for VISA application & payment forms

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Configure credentials
cp .env.example .env
# Edit .env with your Jira and Bitbucket credentials
```

---

## Usage

### Generate test cases from a Jira story

Say this to Claude (replaces `VISASGF-XXXX` with the issue key):

```
Use §1 from prompts/claude_prompts.md for VISASGF-XXXX
```

Or run manually:

```bash
# Fetch the story
python3 jira_reader.py VISASGF-XXXX --json

# Generate Excel from existing JSON
python cli/generate_tests.py --json test_cases/test_cases.json
```

### Check branch health

```bash
python cli/check_branch.py VISASGF-4369
python cli/check_branch.py VISASGF-4369 VISASGF-4370 --partial
```

### Form automation (browser console)

Copy the contents of `src/automation/scripts/application.js` into the browser
console on the VISA application form page. Repeat with `payment.js` on the
payment step.

---

## Project structure

```
src/
├── config.py                        # All URLs, timeouts, credential loading
├── clients/
│   ├── base.py                      # Shared HTTP session with retry
│   ├── jira.py                      # Jira Cloud API
│   └── bitbucket.py                 # Bitbucket Cloud API
├── models/
│   ├── issue.py                     # JiraIssue dataclass
│   ├── test_case.py                 # TestCase / Step dataclasses
│   └── branch_info.py               # BranchInfo dataclass
├── services/
│   └── test_case_generator.py       # JSON → Excel generation logic
└── automation/
    ├── browser.py                   # Playwright task-manager scraping
    └── scripts/
        ├── application.js           # VISA form filler
        └── payment.js               # Payment form filler

cli/
├── generate_tests.py                # Entry point: generate test cases
└── check_branch.py                  # Entry point: branch health report

prompts/
└── claude_prompts.md                # Reusable Claude prompts

test_cases/
├── VISASGF-4167_test_cases.xlsx     # Excel style template (do not edit)
├── test_cases.json                  # Generated — overwritten each run
└── test_cases.xlsx                  # Generated — overwritten each run

# Root-level scripts kept for backward compat (delegate to src/)
jira_reader.py
bitbucket.py
open_chrome.py
```

---

## Credentials

| Key | Where used |
|---|---|
| `JIRA_EMAIL` | Jira API authentication |
| `JIRA_API_TOKEN` | Jira API authentication |
| `JIRA_SITE` | Jira instance URL (default: `https://leadtech.atlassian.net`) |
| `BITBUCKET_USERNAME` | Bitbucket API authentication |
| `BITBUCKET_TOKEN` | Bitbucket app password |
| `BITBUCKET_WORKSPACE` | Bitbucket workspace (default: `grupoblidoo`) |
| `BITBUCKET_REPO` | Bitbucket repo slug (default: `visas-public`) |
| `CHROME_PROFILE_DIR` | Path to Playwright Chrome persistent profile |

Set all of these in `.env` (copy from `.env.example`).
Legacy `token.txt` / `token_jira.txt` files are still supported as a fallback.
