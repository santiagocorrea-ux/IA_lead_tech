# Claude Prompts

Reusable prompts for generating test cases from VISASGF user stories.

> **Project context:** See [visasgf_context.md](visasgf_context.md) for board, sprints, issues, and reference docs. Claude loads it automatically via project memory.

---

## Workflow (how to use this file)

**Single-file, replace-on-every-run.** The folder always contains exactly one JSON and one Excel:

```
test_cases/
├── VISASGF-4167_test_cases.xlsx   # style template (do not edit)
├── visa_testcase_generator.py     # generator script
├── test_cases.json                # ⟵ replaced each run
└── test_cases.xlsx                # ⟵ replaced each run
```

For every new user story:

1. Say to Claude: **`Use §1 from claude_prompts.md for VISASGF-XXXX`**.
2. Claude will:
   - Fetch the story from Jira via `python3 jira_reader.py VISASGF-XXXX --json`
   - Generate test cases from the description + acceptance criteria
   - Overwrite `test_cases/test_cases.json` and `test_cases/test_cases.xlsx`

No need to paste the story — `jira_reader.py` pulls it straight from Jira.

---

## 1. New user story → test cases (main prompt)

Just say this to Claude (replace `VISASGF-XXXX` with the issue key):

```
Use §1 from claude_prompts.md for VISASGF-XXXX
```

When Claude sees that phrase, it will:

1. Fetch the story from Jira:
   ```bash
   python3 jira_reader.py VISASGF-XXXX --json
   ```
2. Parse the `summary`, `description`, and `comments` to extract user story + acceptance criteria.
3. Generate test cases following these rules:
   - Format each step as Action / Data / Expected Result.
   - Cover Happy Path, Unhappy Path, and Edge Cases.
   - One test case per Acceptance Criterion (split when an AC has multiple branches).
   - Include a Regression case for any reference tickets mentioned in the story.
   - Use explicit, verifiable expected results (UI text, API codes, DB/service status, logs).
4. Overwrite `test_cases/test_cases.json` with the new cases (schema: `{"test_cases": [{"name": ..., "steps": [{"action": ..., "data": ..., "expected_result": ...}]}]}`).
5. Run `visa_testcase_generator.py` to overwrite `test_cases/test_cases.xlsx`.
6. Report the issue key, summary, and test case count.

**Fallback:** if Jira is unreachable or the story is not in Jira, include the story text inline after the issue key:

```
Use §1 from claude_prompts.md for VISASGF-XXXX

<paste story text here>
```

---

## 2. Just generate the JSON (no Excel)

When you want to review / edit the JSON before producing the Excel.

```
Use §2 from claude_prompts.md for VISASGF-XXXX
```

Claude fetches the story via `jira_reader.py`, writes `test_cases/test_cases.json`, and stops there (no Excel yet).

---

## 3. Add a single test case to the current story

Use when `test_cases/test_cases.json` already holds the right story and you want one more case.

```
Append a test case to test_cases/test_cases.json for this scenario:

Scenario: {{SCENARIO}}

Then regenerate test_cases/test_cases.xlsx.
```

---

## 4. Regenerate the Excel manually

Run from the project root. Sheet name defaults to `test_cases`, so the single sheet gets replaced each run.

```bash
python3 test_cases/visa_testcase_generator.py \
  --json test_cases/test_cases.json \
  --template test_cases/VISASGF-4167_test_cases.xlsx \
  --output test_cases/test_cases.xlsx
```

---

## 5. Reference example — RDR refund story

First fully worked example. Useful as a template when writing new stories.

<details>
<summary>Story text (click to expand)</summary>

```
BE - CRM - Automatic ticket status update for RDR refunded transactions

As a Product Operations Analyst, I need to automatically update ticket statuses
when refunds are processed through the RDR (Refund Dispute Resolution) system,
so that ticket status accuracy is maintained without manual intervention.

Reference: VISASGF-580
Example tickets: 13795121, 14021163, 14026403

Ticket Status Groups
  Before Processing: Uncompleted, Completed (ticket-level), Pending
  After Processing:  Approved, Denied, Recycled
Final Service Statuses (never overridden): cancelled, processed, used

AC1 — Ticket Status Update
  Before Processing → Cancelled
  After Processing  → no change

AC2 — Additional Services Update
  Before Processing: Cancel THC, Embassy, Fee Protection unless already final.
                     Card → existing secondary ticket cancellation logic.
  After Processing:  Embassy/THC cancel if not final; Fee Protection always
                     cancel; Card cancel if not final; Denied → no action.

AC3 — eSIM service and product never modified.
AC4 — Split Payments: primary = AC1 + AC2; secondary = only affected services.
AC5 — Reprocessing the same RDR must not create inconsistent states.
AC6 — All updates must be logged (ticket, services, old/new status, RDR ref).
```

</details>
