# Email Marketing Skills [![skills.sh](https://skills.sh/b/wakqasahmed/email-marketing-skills)](https://skills.sh/wakqasahmed/email-marketing-skills)

Evidence-grounded skills for email marketing campaigns, lifecycle automation, deliverability, compliance, measurement, and QA.

## Install

```bash
npx skills@latest add wakqasahmed/email-marketing-skills
```

## Ask Your Agent

```text
Create a compliant abandoned-cart email flow for this store. Verify consent, inventory, suppression, tracking, and deliverability first.
```

```text
Plan a welcome series for new subscribers. Include the campaign map, test design, QA checklist, and SEND, HOLD, or BLOCK decision.
```

## Scope
The taxonomy covers recurring editorial mail, welcome/onboarding, lead nurture, promotions, launches, events, ecommerce behavioral flows, post-purchase/customer success, reviews, cross-sell, replenishment/renewal, winback/sunset, transactional mail, B2B outbound, inventory/price alerts, loyalty/referrals, jurisdiction routing, and lifecycle orchestration.

These are composable archetypes rather than a claim that every company uses the same labels. A birthday message, for example, normally combines the promotional skill with lifecycle/date-trigger logic; a trial-expiry message combines onboarding, renewal, and transactional classification.

## Evidence policy
- Every normative instruction in the pack ends with one or more source IDs such as `[GMAIL-01]`.
- `SOURCES.md` maps every source ID to publisher, title, URL, and the claim area it supports.
- Sources are primarily first-party guidance from Gmail, Yahoo, FTC, ICO, Mailchimp, HubSpot, Klaviyo, Braze, Litmus, and Zoom.
- Platform recommendations are baselines, not universal truths; the agent must test them against the actual audience and economics.
- The pack does not promise “best ROI.” It requires measurable objectives, conversion/revenue/pipeline tracking, controlled tests, and holdouts where feasible.

## How an agent should use the pack
1. Load the `00-email-marketing-guardrails` skill.
2. Apply `18-jurisdiction-compliance-routing` before drafting when a recipient is in the US, UK, EEA, or Canada; the sender or sending system is in Canada; or a jurisdiction is unknown or conflicting.
3. Select the closest campaign-specific `SKILL.md`.
4. Load `19-lifecycle-orchestration` when contacts can qualify for multiple flows or channels.
5. Combine multiple skills only when the message genuinely spans campaign types.
6. Collect missing inputs; never fabricate them.
7. Produce the mandatory output and a `SEND`, `HOLD`, or `BLOCK` decision.
8. Re-check the live source before relying on legal or mailbox-provider requirements that may have changed after `2026-07-15`.

## Skills

- `00-email-marketing-guardrails`: mandatory cross-campaign gates; load first.
- `01-newsletter-editorial`: recurring editorial newsletters.
- `02-welcome-onboarding`: new-contact activation and first purchase.
- `03-lead-nurture-education`: permissioned lead education.
- `04-promotional-offer`: targeted commercial offers.
- `05-product-launch`: product and feature launches.
- `06-event-webinar`: event invitations, reminders, and follow-up.
- `07-abandoned-cart`: checkout abandonment recovery.
- `08-browse-abandonment`: product-view follow-up.
- `09-post-purchase-customer-success`: post-purchase and adoption.
- `10-review-feedback-survey`: review, feedback, and survey requests.
- `11-cross-sell-upsell`: cross-sell and upsell campaigns.
- `12-replenishment-renewal`: replenishment and renewal sequences.
- `13-winback-reengagement-sunset`: re-engagement and suppression.
- `14-transactional-service`: essential event-triggered service email.
- `15-b2b-outbound-prospecting`: lawful, low-volume B2B outreach.
- `16-inventory-price-alert`: back-in-stock, low-inventory, and price alerts.
- `17-loyalty-vip-referral`: VIP, loyalty, and referral campaigns.
- `18-jurisdiction-compliance-routing`: sender and recipient jurisdiction facts and operational routing before drafting for US, UK, EEA, Canadian, or unresolved groups.
- `19-lifecycle-orchestration`: contact-level collision and frequency governance across flows.

## Files
- `skills/00-email-marketing-guardrails/SKILL.md`: hard gates for all campaigns (`GLOBAL_GUARDRAILS.md` remains as a pointer).
- `skills/*/SKILL.md`: campaign-specific what/why/when/where/how instructions.
- `SOURCES.md`: verification ledger.
- `SOURCE_INDEX.json`: machine-readable source registry.
- `LINT_REPORT.md`: automated traceability checks.

## Important limitation
This is operational marketing guidance, not legal advice. Laws vary by recipient, sender, message purpose, and jurisdiction; unresolved legal-basis questions must produce `BLOCK` and be escalated to qualified counsel.

## Validation

```bash
python3 scripts/validate-plugin.py
python3 scripts/validate-orchestration.py
scripts/list-skills.sh
```
