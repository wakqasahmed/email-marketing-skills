---
name: 14-transactional-service
description: Create essential event-triggered messages such as verification, password reset, receipt, shipping, account, security, and service-status emails.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Transactional and Service Email

Use this skill only after applying `../../GLOBAL_GUARDRAILS.md`.

## What and why
A transactional email delivers essential information tied to a user action, purchase, account, security event, or service relationship rather than a marketing conversion. [BRAZE-TRANS-01][MC-PERM-01]

## When and where
- Trigger immediately from the authoritative system event and send only to the affected recipient. [BRAZE-TRIG-01][BRAZE-TRANS-01]
- Use a dedicated transactional stream and template so essential information is not delayed or obscured by promotional content; where infrastructure permits, separate transactional and marketing traffic for independent reputation control. [BRAZE-TRANS-01][AWS-SES-SEP-01]

## How
- Put the essential fact and required action first: what happened, item/account, amount or status, timestamp, next step, support path, and security guidance where relevant. [BRAZE-TRANS-01]
- Keep the subject and sender accurate and recognizable, and never disguise marketing as a receipt, security alert, or reply. [FTC-01]
- Keep pure transactional messages free of marketing content; if commercial content changes the primary purpose, apply marketing consent and opt-out rules. [BRAZE-TRANS-01][FTC-01]
- Validate all dynamic data, prevent raw merge-tag exposure, and test links and rendering before deployment. [LIT-QA-01][LIT-TEST-01]
- Monitor delivery success, latency, bounces, authentication, support contacts, completion of the required action, and failure/retry paths. [GMAIL-03][MC-REPORT-01][AWS-SES-MON-01]

## Do / Don't quick reference
**Do**
- Trigger immediately from the authoritative system event, only to the affected recipient. [BRAZE-TRIG-01][BRAZE-TRANS-01]
- Put the essential fact and required action first. [BRAZE-TRANS-01]
- Separate transactional and marketing traffic for independent reputation where infrastructure permits. [BRAZE-TRANS-01][AWS-SES-SEP-01]
- Monitor delivery success, latency, bounces, and authentication continuously. [GMAIL-03][AWS-SES-MON-01]

**Don't**
- Don't disguise marketing as a receipt, security alert, or reply. [FTC-01]
- Don't add commercial content that changes the primary purpose without applying marketing consent and opt-out rules. [BRAZE-TRANS-01][FTC-01]
- Don't ship unvalidated dynamic data or raw merge tags. [LIT-QA-01]
- Don't queue essential messages behind marketing volume. [BRAZE-TRANS-01][AWS-SES-SEP-01]

## Mandatory output
Return all of the following:
1. Campaign objective and one primary business KPI.
2. Audience, eligibility, exclusions, and consent/lawful-basis note.
3. Trigger or send schedule, including exit and suppression rules.
4. Message map showing the job of each email, subject-line hypotheses, body outline, personalization, and one primary CTA.
5. Measurement plan with UTMs, conversion event, attribution window, and guardrail metrics.
6. Test plan that changes one major variable at a time and names the winning metric.
7. Pre-send QA checklist and a final `SEND`, `HOLD`, or `BLOCK` decision.
8. A source list containing every citation ID used.

## Agent restrictions
- Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims. [FTC-01][BRAZE-STRAT-01]
- Never infer consent merely because an address exists; verify the permitted purpose, channel, source, jurisdiction, and suppression status. [ICO-01][ICO-02][HUB-CONSENT-01]
- Never optimize for opens alone; use clicks, conversions, revenue, retention, qualified replies, or pipeline as the primary outcome. [LIT-MPP-01][MC-CONV-01][BRAZE-METRIC-01]
- Never claim a universal best send time; use recipient-level optimization or a controlled timing test. [MC-TIME-01][MC-AB-01]
- Never send until authentication, suppression, tracking, rendering, links, personalization fallbacks, and accessibility checks pass. [GMAIL-01][YAHOO-01][LIT-QA-01][LIT-TEST-01]
