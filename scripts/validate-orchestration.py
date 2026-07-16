#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = root / "skills" / "18-lifecycle-orchestration" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing lifecycle orchestration skill")

required_lines = {
    "Contact-level decision order": {
        "contact-level decision": "Evaluate each contact at reservation time and again immediately before send, recording the input snapshot, winning candidate, rejected candidates, reason codes, next eligible time, and policy version. [HUB-WF-01][BRAZE-STRAT-01]",
        "service priority": "6. When event-bound service information is verified, essential service messages bypass marketing scheduling, quiet periods, and marketing caps; they must never carry marketing content or reset, evade, or consume marketing caps. [BRAZE-TRANS-01][FTC-01]",
    },
    "Event precedence and ownership": {
        "event precedence": "- Resolve remaining marketing conflicts with a published precedence table based on current intent and message expiry, not whichever automation runs first; use this default only until the business documents a stricter table: requested time-critical alert, checkout/cart recovery, onboarding or post-purchase task, replenishment/renewal, targeted promotion or launch, browse, then winback/editorial. [BRAZE-TRIG-01][KL-CART-01][KL-BROWSE-01][BRAZE-STRAT-01]",
    },
    "Pressure, suppression, and experiments": {
        "global and segment caps": "- Count sent and already reserved marketing messages across channels in each rolling global and segment window before reserving another; a campaign-specific allowance may tighten but never loosen an applicable global or preference limit. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]",
        "quiet periods": "- Defer non-urgent marketing to the first eligible local time after the quiet period only if the trigger remains valid; when timezone is unknown, use the documented conservative fallback or return `HOLD`. [BRAZE-STRAT-01][HUB-WF-01]",
        "channel preferences": "- Apply the recipient's permitted channels and stated topic/frequency choices first, choose only an allowed channel, and do not substitute email, SMS, push, or another channel without permission for that channel and purpose. [ICO-02][BRAZE-STRAT-01]",
        "atomic deduplication": "- Build the deduplication key from contact, channel, purpose, authoritative event or subject entity, and flow step; atomically reserve it and suppress any matching reserved or sent message for the configured validity window. [BRAZE-TRIG-01][HUB-WF-01]",
        "recent-purchase suppression": "- Define recent-purchase suppression by product/category, campaign purpose, and a documented lookback window; suppress stale acquisition, browse, cart, price, or incompatible recommendation messages while preserving relevant service and post-purchase information. [KL-BROWSE-01][KL-LOWSTOCK-01][KL-XSELL-01][BRAZE-TRANS-01]",
        "sampled control exclusion": "- Create a sampled control segment for the test window and exclude it from every marketing treatment covered by the test; preserve eligibility for transactional and essential service messages. [KL-SEGTEST-01]",
    },
    "Mandatory output": {
        "campaign calendar": "4. Campaign calendar: date/time and timezone, campaign/flow, segment, channel, expected eligible volume, cap budget, holdout, owner, dependencies, and collision notes. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]",
        "monitoring": "5. Monitoring and exception report: sends/reservations by contact and flow, cap and quiet-period blocks, collisions won/lost, duplicate attempts, stale-event drops, purchase suppressions, holdout leakage, service latency, delivery/bounce/complaint metrics, and alerts with owners. [AWS-SES-MON-01][GMAIL-03][BRAZE-METRIC-01]",
    },
}


def sections(text: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:]
            result[current] = set()
        elif current and line:
            result[current].add(line)
    return result


def validate(text: str) -> list[str]:
    parsed = sections(text)
    missing = []
    for section, contracts in required_lines.items():
        section_lines = parsed.get(section, set())
        missing.extend(
            label for label, required_line in contracts.items() if required_line not in section_lines
        )
    return missing


text = skill.read_text()
missing = validate(text)
if missing:
    raise SystemExit("Lifecycle orchestration contract missing: " + ", ".join(missing))

mutations = {
    "event precedence": "published precedence table",
    "atomic deduplication": "atomically reserve it and ",
    "sampled control exclusion": "exclude it from every marketing treatment covered by the test",
}
for expected_failure, deleted_text in mutations.items():
    mutated = text.replace(deleted_text, "", 1)
    if expected_failure not in validate(mutated):
        raise SystemExit(f"Mutation check failed: deleting {expected_failure} was accepted")

print("lifecycle orchestration contract OK")
