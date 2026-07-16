---
name: 18-lifecycle-orchestration
description: Resolve contact-level collisions across lifecycle flows with deterministic ownership, frequency, suppression, holdout, calendar, and monitoring rules.
version: 1.0.0
last_reviewed: 2026-07-16
---

# Lifecycle Orchestration and Frequency Governance

Use this skill after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`) whenever a contact can qualify for more than one campaign or channel.

## What and why
A lifecycle orchestrator evaluates all eligible messages together so current customer state, permission, preferences, and campaign pressure produce one auditable contact-level decision rather than several independently valid sends. [BRAZE-STRAT-01][HUB-WF-01]

## Required inputs
- Collect the contact ID, timezone, jurisdiction, consent and suppression state by channel and purpose, channel preferences, segment memberships, lifecycle state, authoritative events, active flow memberships, reserved and completed sends, purchase history, holdout assignments, and configured quiet periods and caps; return `HOLD` rather than inventing missing values. [ICO-02][BRAZE-STRAT-01][HUB-WF-01]
- Collect every candidate's message class, purpose, channel, flow and step ID, trigger event and timestamp, subject entity such as cart/order/product, expiry, exit conditions, deduplication key, and experiment ID. [BRAZE-TRANS-01][BRAZE-TRIG-01][HUB-WF-01]
- Define numeric global and segment caps from documented business policy and recipient expectations; do not present one universal cadence as correct for every audience. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]

## Contact-level decision order
Evaluate each contact at reservation time and again immediately before send, recording the input snapshot, winning candidate, rejected candidates, reason codes, next eligible time, and policy version. [HUB-WF-01][BRAZE-STRAT-01]

1. Apply legal-basis, consent, unsubscribe, complaint, bounce, identity, authentication, and factual hard gates from the global guardrails; a failed hard gate is `BLOCK`, not a lower-priority send. [ICO-02][GMAIL-01][FTC-01]
2. Classify every candidate by primary purpose as essential service, marketing, or mixed; treat mixed messages as marketing and never relabel a promotion to win priority. [BRAZE-TRANS-01][FTC-01]
3. Remove candidates invalidated by a newer authoritative event, an exit condition, loss of ownership, recent purchase, deduplication, or a relevant experiment holdout. [BRAZE-TRIG-01][HUB-WF-01][KL-BROWSE-01][KL-SEGTEST-01]
4. For remaining marketing candidates, enforce the contact's channel preference, quiet period, and the global and every applicable segment cap; the most restrictive applicable rule wins. [ICO-02][BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
5. Select at most one marketing candidate for the decision window using the declared ownership and precedence rules below; reschedule only while its trigger remains valid and its expiry and exit conditions permit, otherwise drop it. [HUB-WF-01][BRAZE-TRIG-01]
6. When event-bound service information is verified, essential service messages bypass marketing scheduling, quiet periods, and marketing caps; they must never carry marketing content or reset, evade, or consume marketing caps. [BRAZE-TRANS-01][FTC-01]

## Event precedence and ownership
- Let the newest authoritative event update state before campaign priority is considered: purchase exits cart, browse, and incompatible promotion candidates; checkout exits browse; registration exits invitation; renewal exits renewal reminders; opt-out or complaint exits all affected marketing. [HUB-WF-01][KL-CART-01][KL-BROWSE-01][GMAIL-01]
- Define one owning flow for each contact, objective, and subject entity, and persist its entry event, entry time, current step, exit conditions, and ownership expiry; a non-owner may not send another message for the same objective and entity. [HUB-WF-01][BRAZE-TRIG-01]
- Resolve remaining marketing conflicts with a published precedence table based on current intent and message expiry, not whichever automation runs first; use this default only until the business documents a stricter table: requested time-critical alert, checkout/cart recovery, onboarding or post-purchase task, replenishment/renewal, targeted promotion or launch, browse, then winback/editorial. [BRAZE-TRIG-01][KL-CART-01][KL-BROWSE-01][BRAZE-STRAT-01]
- Break equal-priority ties by earliest real expiry, then most recent specific trigger, then oldest reservation request; log the tie-break and never invent urgency. [FTC-01][BRAZE-TRIG-01]
- Release ownership immediately when the goal completes, the trigger expires, the contact becomes ineligible, or the contact opts out or complains; re-entry requires a new qualifying event and the flow's re-entry rule. [HUB-WF-01][GMAIL-01]

## Pressure, suppression, and experiments
- Count sent and already reserved marketing messages across channels in each rolling global and segment window before reserving another; a campaign-specific allowance may tighten but never loosen an applicable global or preference limit. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
- Apply the recipient's permitted channels and stated topic/frequency choices first, choose only an allowed channel, and do not substitute email, SMS, push, or another channel without permission for that channel and purpose. [ICO-02][BRAZE-STRAT-01]
- Defer non-urgent marketing to the first eligible local time after the quiet period only if the trigger remains valid; when timezone is unknown, use the documented conservative fallback or return `HOLD`. [BRAZE-STRAT-01][HUB-WF-01]
- Build the deduplication key from contact, channel, purpose, authoritative event or subject entity, and flow step; atomically reserve it and suppress any matching reserved or sent message for the configured validity window. [BRAZE-TRIG-01][HUB-WF-01]
- Define recent-purchase suppression by product/category, campaign purpose, and a documented lookback window; suppress stale acquisition, browse, cart, price, or incompatible recommendation messages while preserving relevant service and post-purchase information. [KL-BROWSE-01][KL-LOWSTOCK-01][KL-XSELL-01][BRAZE-TRANS-01]
- Assign a stable holdout before flow entry, store experiment ID, unit, variant, start/end, and eligibility, and exclude that unit from every marketing treatment covered by the experiment; never withhold essential service messages. [KL-SEGTEST-01][BRAZE-TRANS-01]

## Mandatory output
Return all of the following:

1. Policy header: policy version, evaluation timestamp, decision window, timezone fallback, configured global/segment caps, quiet periods, channel-preference source, and data freshness. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
2. Contact-level decision table: contact, candidate, class, authoritative event, owner, eligibility, pressure counts, holdout, deduplication result, decision (`SEND`, `DEFER`, `DROP`, or `BLOCK`), reason code, and next eligible time. [HUB-WF-01][BRAZE-TRANS-01]
3. Conflict matrix: each flow pair, governing event precedence, owner, tie-break, exit/re-entry rule, recent-purchase rule, and whether the loser is deferred or dropped. [HUB-WF-01][BRAZE-TRIG-01]
4. Campaign calendar: date/time and timezone, campaign/flow, segment, channel, expected eligible volume, cap budget, holdout, owner, dependencies, and collision notes. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
5. Monitoring and exception report: sends/reservations by contact and flow, cap and quiet-period blocks, collisions won/lost, duplicate attempts, stale-event drops, purchase suppressions, holdout leakage, service latency, delivery/bounce/complaint metrics, and alerts with owners. [AWS-SES-MON-01][GMAIL-03][BRAZE-METRIC-01]
6. One worked contact trace showing the ordered input snapshot, every rejected candidate and reason code, the winning decision, and the next reevaluation trigger. [HUB-WF-01][BRAZE-TRIG-01]
7. A final `SEND`, `HOLD`, or `BLOCK` decision for policy readiness and a source list containing every citation ID used. [LIT-QA-01][GMAIL-01]

## Agent restrictions
- Never invent consent, caps, quiet hours, preferences, event timestamps, ownership, purchase windows, or holdout assignments; unresolved hard-gate data is `BLOCK` and unresolved operational policy is `HOLD`. [ICO-02][GMAIL-01][BRAZE-STRAT-01]
- Never let campaign-level settings loosen a global or recipient-specific restriction, and never evaluate flows independently when their decision windows overlap. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
- Never use an essential-service label, transactional stream, or urgent priority to carry promotion or bypass marketing consent, suppression, preferences, caps, quiet periods, deduplication, or holdouts. [BRAZE-TRANS-01][FTC-01]
- Never withhold, delay behind marketing, or include essential service messages in marketing experiments or cap counts; monitor their latency and delivery separately. [BRAZE-TRANS-01][AWS-SES-SEP-01][AWS-SES-MON-01]
