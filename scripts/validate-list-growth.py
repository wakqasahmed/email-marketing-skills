#!/usr/bin/env python3
from pathlib import Path


root = Path(__file__).resolve().parents[1]
skill = root / "skills" / "20-list-growth-signup-preferences" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing list-growth signup-preferences skill")

required_lines = {
    "Consent-capture contract": {
        "guardrails and routing": "- Apply `00-email-marketing-guardrails` first and run `18-jurisdiction-compliance-routing` before publishing a form; return `HOLD` while required routing facts are collectible and `BLOCK` when the applicable basis or capture requirement cannot be verified. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]",
        "complete record": "- Persist the contact identifier, signup source and form ID, exact consent statement and form version, timestamp, jurisdiction facts, channel, purpose, selected preferences, capture method, confirmation state, and later withdrawals or changes; do not reduce the audit trail to a generic consent flag. [ICO-CONSENT-01][KL-CONSENT-01][MC-PROFILE-01]",
        "expectations": "- Name the sender, channel, content or purpose, and expected frequency at capture, link the applicable privacy information, and use separate unbundled choices where purposes or channels differ. [ICO-02][ICO-04][KL-FORMS-01]",
        "address verification": "- Validate address syntax and ask the person to correct apparent typos; use confirmation or double opt-in when stronger address ownership and intent verification is appropriate, and never silently rewrite an address or treat an unconfirmed contact as subscribed. [KL-DOI-01][MC-DOI-01]",
    },
    "Double opt-in and welcome handoff": {
        "conditional use": "- Choose single or double opt-in from the applicable jurisdiction route, risk, list-quality needs, and documented business policy; double opt-in is a strong verification practice, not a universal legal requirement. [MC-DOI-01][KL-DOI-01][ICO-01]",
        "pending state": "- For double opt-in, store `PENDING_CONFIRMATION` after form submission, send only the confirmation message, and move to `SUBSCRIBED` only after the person confirms; an expired or absent confirmation remains ineligible for marketing. [MC-DOI-01][KL-DOI-01]",
        "welcome handoff": "- Hand a `SUBSCRIBED` record and its source, statement version, confirmation timestamp, jurisdiction, channel, purpose, and preferences to `02-welcome-onboarding`; never trigger the marketing welcome flow from `PENDING_CONFIRMATION`. [KL-DOI-01][KL-WELCOME-01][ICO-CONSENT-01]",
    },
    "Preferences and lead magnets": {
        "preferences": "- Offer meaningful topic, channel, and frequency choices, preserve a clear unsubscribe-all option, apply changes to future eligibility and orchestration, and record the changed values and timestamp without overwriting the prior audit trail. [BRAZE-STRAT-01][ICO-CONSENT-01]",
        "lead magnet": "- Describe the promised resource and any marketing subscription separately and truthfully, disclose what follows after signup, and deliver the resource as promised without presenting access as proof of consent to undisclosed marketing. [FTC-01][ICO-02][KL-WELCOME-01]",
        "prohibited acquisition": "- Never replace first-party capture with bought, rented, scraped, harvested, publicly copied, or otherwise unverifiable addresses, and never invent conversion claims or unsupported signup tactics. [MC-LISTS-01][ICO-04][FTC-01]",
    },
    "Behavioral acceptance traces": {
        "incomplete record": "| Incomplete consent record | Signup lacks the statement version or channel. | `HOLD: CONSENT_RECORD_INCOMPLETE`; collect the missing field and do not mark the contact subscribed. [ICO-CONSENT-01][ICO-02] |",
        "pending confirmation": "| Double opt-in pending | Form submission is valid but confirmation has not occurred. | Store `PENDING_CONFIRMATION`; permit only the confirmation message and exclude the contact from marketing and welcome. [MC-DOI-01][KL-DOI-01] |",
        "preference change": "| Preference change | A subscribed contact changes from weekly product news to monthly education only. | Timestamp the new choices, retain the prior record, update eligibility and orchestration, and exclude weekly product news. [BRAZE-STRAT-01][ICO-CONSENT-01] |",
        "lead magnet": "| Lead magnet | A form promises a guide and separately offers clearly described email marketing. | Deliver the guide as promised; subscribe only when the marketing choice and applicable route are valid, with no hidden or bundled permission. [FTC-01][ICO-02][KL-WELCOME-01] |",
        "welcome handoff": "| Confirmed welcome handoff | A pending contact confirms before expiry. | Record confirmation, set `SUBSCRIBED`, and pass the complete consent and preference record to `02-welcome-onboarding`. [KL-DOI-01][KL-WELCOME-01][ICO-CONSENT-01] |",
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
    raise SystemExit("List-growth contract missing: " + ", ".join(missing))

mutations = {
    "complete record": "exact consent statement and form version",
    "address verification": "never silently rewrite an address",
    "conditional use": "not a universal legal requirement",
    "pending state": "send only the confirmation message",
    "welcome handoff": "never trigger the marketing welcome flow from `PENDING_CONFIRMATION`",
    "preferences": "without overwriting the prior audit trail",
    "lead magnet": "without presenting access as proof of consent to undisclosed marketing",
    "prohibited acquisition": "bought, rented, scraped, harvested, publicly copied",
    "incomplete record": "`HOLD: CONSENT_RECORD_INCOMPLETE`",
    "pending confirmation": "exclude the contact from marketing and welcome",
    "preference change": "exclude weekly product news",
    "welcome handoff": "pass the complete consent and preference record",
}
for expected_failure, deleted_text in mutations.items():
    mutated = text.replace(deleted_text, "", 1)
    if mutated == text:
        raise SystemExit(f"Mutation fixture missing: {expected_failure}")
    if expected_failure not in validate(mutated):
        raise SystemExit(f"Mutation check failed: deleting {expected_failure} was accepted")

print(f"list-growth consent contract OK: {len(mutations)} mutations rejected")
