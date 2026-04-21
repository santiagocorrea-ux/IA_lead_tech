# Claude Prompts

A collection of reusable prompts for Claude.

---

## Test Case Generation

```
python3 test_cases/visa_testcase_generator.py \
  --json test_cases/sample_test_cases.json \
  --template test_cases/VISASGF-4167_test_cases.xlsx \
  --output test_cases/generated_test_cases.xlsx
```

---

## Prompts

### Analyze user story and create test cases

```
analyse this user story

BE - CRM - Automatic ticket status update for RDR refunded transactions

Key details
Description

As a Product Operations Analyst,
I need to automatically update ticket statuses when refunds are processed through the RDR (Refund Dispute Resolution) system,
so that ticket status accuracy is maintained without manual intervention.

Resources
Reference: VISASGF-580: BE - Automate RDR Refund creation in CRM to prevent duplicate refunds
Examples of RDR refunded tickets before processing: 13795121, 14021163, 14026403

Context
- RDR refunds are already recorded in CRM (see: VISASGF-580)
- Additional services are managed via product_service
- All services support: persisted statuses, API/manual updates, automation updates
- No strict state machine exists → logic must be defensive and generic

Definitions
Ticket Status Groups
Before Processing: Uncompleted, Completed (ticket-level), Pending
After Processing: Approved, Denied, Recycled

Final Service Statuses (No Action Required): cancelled, processed, used
These statuses must not be overridden unless explicitly stated.

Acceptance Criteria

For single payment tickets
AC 1: Ticket Status Update
  Given a ticket is refunded via RDR
  When the refund is recorded in CRM
  - If ticket is Before Processing → set to Cancelled
  - If ticket is After Processing → no change

AC 2: Additional Services Update
  Given a refunded ticket with additional services
  Before Processing:
    - Cancel all services (THC, Embassy, Fee Protection) unless already final
    - Card → follow existing secondary ticket cancellation logic
  After Processing:
    - Embassy & THC → cancel if not in final status
    - Fee Protection → always cancel
    - Card → cancel if not final
    - If ticket is Denied → no action (handled by existing logic)

AC 3: eSIM Exception
  - eSIM service and product → never modified

AC 4: Split Payments
  - Primary transaction refunded → apply AC1 + AC2
  - Secondary transaction refunded:
    - Ticket → no change
    - Only affected services → cancel if not final

AC 5: Safe processing for RDR
  - Reprocessing the same RDR must not create inconsistent states

AC 6: Logging
  - All updates must be logged (ticket, services, old/new status, RDR reference)

create the test cases and using the folder test_cases
```

