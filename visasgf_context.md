# VISASGF — Context Pack for AI Test Case Generation

## 1. Project & Board

| Field | Value |
|---|---|
| Project key | VISASGF |
| Project name | Visas (GF) |
| Board URL | https://leadtech.atlassian.net/jira/software/c/projects/VISASGF/boards/7029 |
| Active sprint | Sprint 004 - #BE FY26 #17-18 (2026-04-20 → 2026-05-03) |
| Previous sprint | Sprint 003 - #BE FY26 #15-16 (Closed 2026-04-20) |

## 2. Domain Context

This board covers:
- **Backend Engineering** — RabbitMQ provisioning, visas-email refactors, CRM behaviour
- **Frontend Engineering** — styleweb changes, translations, form behaviour
- **CRM (Visas)** — views, filters, Elastic/CRM lists, status labels, multitraveler
- **Infrastructure** — devk8s / visas-dev-k8s Kubernetes environments

## 3. Reference Docs

| Topic | URL |
|---|---|
| RabbitMQ overview | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/4682121223/RabbitMQ |
| Queues + Supervisor operations | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/2815098993/Gesti+n+de+colas+RabbitMQ+y+Supervisor |
| Test env dependencies (rabbit.visas.sandbox) | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/4871618635/Repositorios+y+dependencias |
| XRAY + AI QA process | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/4773052447/Estrategia+y+manual+de+XRAY+IA+en+QA+Visados |
| CRM page overview | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/4229038083/P+gina+CRM |
| Latin characters validation regex | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/3968172040/Gu+a+de+uso+para+alerta+de+car+cteres+latinos |
| Trustpilot popup expected behaviour | https://leadtech.atlassian.net/wiki/spaces/VIS/pages/4712529987/Pop+up+Trustpilot+en+la+Thankyou |

## 4. Test Case Step Format (required)

Each step must have three fields:
- **Action** — what to do
- **Data** — inputs, parameters, environment details
- **Expected Result** — explicit, verifiable outcome (UI text, API response codes, DB states, logs, queue metrics)

Include Happy Path, Unhappy Path, and Edge Cases when ACs mention them.

## 5. Issue Catalog

### VISASGF-2226 · User Story · Major · 8 SP · Backend Eng
**Provision RabbitMQ queues and exchanges in devk8s environment** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-2226  
Consumers in devk8s fail due to missing RabbitMQ queues. Goal: provision exchanges/queues/bindings in devk8s (Terraform/Helm/Operator).  
**AC:**
1. Required exchanges/queues auto-created on startup or via provisioning scripts.
2. Consumers bind without "404 Not Found" channel errors.
3. If provisioning fails, RabbitMQ pod stays non-ready or logs "Provisioning Failed".
4. Permissions (vhosts/users) in devk8s match consumer needs; no "403 Access Refused".

---

### VISASGF-2261 · User Story · Major · 8 SP · Backend Eng (visas-email)
**Refactor SendMessageJob to persist messages and reduce failed_jobs payload size** — Ready for Work  
https://leadtech.atlassian.net/browse/VISASGF-2261  
**AC:**
1. Persist message in `messages` table before dispatch; initial status `pending/queued`.
2. Job receives only `message_id`; updates status to `sent` on success.
3. Add `delivery_status` column with optimized migration strategy.
4. On failure: `failed_jobs` stores only `message_id`; messages status stays `pending` or becomes `failed` after retries.
5. Handle case where job starts but `message_id` not found.

---

### VISASGF-1868 · Maintenance · Major · 13 SP · Backend Eng
**Eliminar swiftmailer de visas-email** — In Progress  
https://leadtech.atlassian.net/browse/VISASGF-1868

---

### VISASGF-2264 · User Story · Major · 5 SP · Backend Eng
**Implement Lazy Loading for Sites in VisasApiSiteService** — Ready for Work  
https://leadtech.atlassian.net/browse/VISASGF-2264

---

### VISASGF-1054 · User Story · Major · 5 SP · Frontend Eng
**Añadir pop up de Trustpilot en styleweb visasyst** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-1054  
**AC:** Trustpilot popup triggers on thankyou or after completing profile in visasyst.com styleweb.

---

### VISASGF-2386 · User Story · Minor · 5 SP · Frontend Eng
**FE - UKETA - /application - Make field parentName optional** — Waiting for Approval  
https://leadtech.atlassian.net/browse/VISASGF-2386

---

### VISASGF-2385 · User Story · Minor · 3 SP · Backend Eng
**BE - UKETA - Make parentName optional + update CRMview fields** — Pending  
https://leadtech.atlassian.net/browse/VISASGF-2385

---

### VISASGF-2666 · User Story · Minor · 3 SP · Frontend Eng
**FE - All visas - Implement changes in translation priority** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-2666

---

### VISASGF-2253 · User Story · Minor · 13 SP · Backend Eng
**BE - EG - Implement passport MRZ extraction + CRM overwrite** — In Review  
https://leadtech.atlassian.net/browse/VISASGF-2253

---

### VISASGF-2404 · User Story · Minor · 5 SP · Frontend Eng
**Fix translations "Please use latin characters" (kr,tw)** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-2404  
KR/TW currently show generic invalid messages; must instruct to use Latin characters.

---

### VISASGF-3394 · User Story · Minor · 5 SP · Backend Eng
**BE - ALL VISAS - CRM - Multitraveler Filter in CRM** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-3394

---

### VISASGF-3978 · User Story · Minor · 3 SP · Backend Eng
**BE - UKETA - Add "Discarded" label in CRM products/visas View** — In Progress  
https://leadtech.atlassian.net/browse/VISASGF-3978

---

### VISASGF-4594 · Bug · Critical · 3 SP · Backend Eng
**DOET - Profile page fails after payment** — Waiting for Approval  
https://leadtech.atlassian.net/browse/VISASGF-4594

---

### VISASGF-1612 · Bug · Minor · 3 SP · Backend Eng
**KE - CRM dates format incorrect** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-1612

---

### VISASGF-1512 · Bug · Minor · 5 SP · Backend Eng
**PHOHP - completion % must exclude hidden fields** — Ready for Testing  
https://leadtech.atlassian.net/browse/VISASGF-1512

---

### VISASGF-2769 · Bug · Minor · 5 SP · Frontend Eng
**PHOHP /profile - Flight Number "Other" not saved in non-English** — Waiting for Approval  
https://leadtech.atlassian.net/browse/VISASGF-2769  
Steps to reproduce: set language to non-English → Travel Information → Flight Number → select Other → proceed → return and verify.  
**Expected:** "Other" persists regardless of locale.

---

### VISASGF-3634 · Bug · Minor · 5 SP · Frontend Eng
**UKETA /application - Block paste in "Confirm Email Address"** — Waiting for Approval  
https://leadtech.atlassian.net/browse/VISASGF-3634  
**Expected:** Paste blocked via keyboard and context menu.

---

### VISASGF-2327 · User Story · Minor · 3 SP · Backend Eng
**IN - Add new port of arrival list** — Waiting for Approval  
https://leadtech.atlassian.net/browse/VISASGF-2327

---

### VISASGF-1143 · User Story · Major · 21 SP · Frontend Eng
**FE - Service Card Activation in KH (profile card)** — Check In Prod  
https://leadtech.atlassian.net/browse/VISASGF-1143

---

### VISASGF-1142 · User Story · Major · 21 SP · Backend Eng
**BE - Service Card Activation in KH (/profile card /CRM)** — Check In Prod  
https://leadtech.atlassian.net/browse/VISASGF-1142

---

### VISASGF-1252 · Bug · Minor · 5 SP · Frontend Eng
**Incorrect translation of service priority string (cn,tw)** — In Progress  
https://leadtech.atlassian.net/browse/VISASGF-1252

---

### VISASGF-4181 · User Story · Minor · 5 SP · Frontend Eng
**FE - ESTA - Reduce Mandatory Questions section** — In Progress  
https://leadtech.atlassian.net/browse/VISASGF-4181  
(see also VISASGF-3956)

---

### VISASGF-2151 · User Story · Minor · 13 SP · Frontend Eng
**FE - Automate profile card creation** — Pending  
https://leadtech.atlassian.net/browse/VISASGF-2151

---

### VISASGF-667 · Maintenance · Major · 3 SP · Backend Eng
**[Spike] Investigation for S3 header image deduplication by productType** — Ready for Work  
https://leadtech.atlassian.net/browse/VISASGF-667

## 6. Standard Prompt Template

To generate test cases for a specific issue, use:

```
Using the VISASGF project context (visasgf_context.md), generate test cases for [VISASGF-XXXX].
Format each step as: Action / Data / Expected Result.
Cover: Happy Path, Unhappy Path, Edge Cases.
Output as JSON compatible with rdr_refund_test_cases.json format for use with visa_testcase_generator.py.
Save output to test_cases/[issue-key]_test_cases.json and append to test_cases/all_test_cases.xlsx.
```
