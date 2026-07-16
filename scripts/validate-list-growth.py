#!/usr/bin/env python3
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
skill = root / "skills" / "20-list-growth-signup-preferences" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing list-growth signup-preferences skill")

required_contracts = {
    "Consent-capture contract": {
        "guardrails and routing": ("00-email-marketing-guardrails", "18-jurisdiction-compliance-routing", "`HOLD`", "`BLOCK`"),
        "complete record": ("exact consent statement", "form version", "channel", "purpose", "confirmation state"),
        "expectations": ("sender", "channel", "purpose", "frequency", "separate unbundled choices"),
        "address verification": ("confirmation or double opt-in", "address ownership", "unconfirmed grant", "subscribed"),
    },
    "Double opt-in and welcome handoff": {
        "conditional use": ("single or double opt-in", "jurisdiction", "risk", "not a universal legal requirement"),
        "scoped pending state": ("`PENDING_CONFIRMATION`", "list, channel, and purpose", "only the confirmation message for that pending grant", "unrelated eligible service"),
        "scoped welcome handoff": ("`SUBSCRIBED`", "same list, channel, and purpose", "`02-welcome-onboarding`", "matching `PENDING_CONFIRMATION`"),
    },
    "Preferences and lead magnets": {
        "preferences": ("topic, channel, and frequency", "unsubscribe-all", "prior audit trail"),
        "lead magnet": ("resource", "marketing subscription separately", "without presenting access as proof of consent"),
        "prohibited acquisition": ("bought", "rented", "scraped", "harvested", "publicly copied"),
    },
}

trace_requirements = {
    "Incomplete consent record": {
        "given": ("lacks", "statement version", "channel"),
        "outcome": ("`HOLD: CONSENT_RECORD_INCOMPLETE`", "do not mark"),
    },
    "Double opt-in pending": {
        "given": ("list, email channel, and product-news purpose", "confirmation has not occurred"),
        "outcome": ("`PENDING_CONFIRMATION`", "confirmation message", "matching marketing and welcome"),
    },
    "Cross-purpose confirmation isolation": {
        "given": ("pending", "new product-news list", "existing education permission", "order receipt"),
        "outcome": ("new grant remains pending", "education permission and receipt remain eligible", "does not grant product-news marketing"),
    },
    "Preference change": {
        "given": ("weekly product news", "monthly education only"),
        "outcome": ("retain the prior record", "exclude weekly product news"),
    },
    "Lead magnet": {
        "given": ("guide", "separately offers", "email marketing"),
        "outcome": ("Deliver the guide", "subscribe only when", "no hidden or bundled permission"),
    },
    "Prohibited acquisition": {
        "given": ("bought or scraped", "marketing audience"),
        "outcome": ("`BLOCK: UNVERIFIABLE_ACQUISITION`", "do not import or send"),
    },
    "Confirmed welcome handoff": {
        "given": ("pending grant", "same list, channel, and purpose", "confirms"),
        "outcome": ("set that grant to `SUBSCRIBED`", "`02-welcome-onboarding`"),
    },
}

contradictions = {
    "unconfirmed subscription": re.compile(r"mark (?:every|all) form submissions? (?:as )?subscribed", re.I),
    "permissionless acquisition": re.compile(r"bought(?:\s+and|\s*,)?\s*scraped addresses are permitted", re.I),
    "lead-magnet inferred consent": re.compile(r"lead[- ]magnet download proves consent", re.I),
}


def sections(text: str) -> dict[str, str]:
    result: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:]
            result[current] = []
        elif current:
            result[current].append(line)
    return {name: "\n".join(lines) for name, lines in result.items()}


def traces(section: str) -> dict[str, tuple[str, str]]:
    result = {}
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] not in {"Trace", "---"}:
            result[cells[0]] = (cells[1], cells[2])
    return result


def validate(text: str) -> list[str]:
    errors = []
    parsed = sections(text)
    for section, contracts in required_contracts.items():
        section_text = parsed.get(section, "")
        for label, terms in contracts.items():
            if not all(term in section_text for term in terms):
                errors.append(label)

    parsed_traces = traces(parsed.get("Behavioral acceptance traces", ""))
    for label, requirements in trace_requirements.items():
        given, outcome = parsed_traces.get(label, ("", ""))
        if not all(term.lower() in given.lower() for term in requirements["given"]):
            errors.append(f"{label} input")
        if not all(term.lower() in outcome.lower() for term in requirements["outcome"]):
            errors.append(f"{label} outcome")

    for label, pattern in contradictions.items():
        if pattern.search(text):
            errors.append(f"contradiction: {label}")
    return errors


text = skill.read_text()
errors = validate(text)
if errors:
    raise SystemExit("List-growth contract invalid: " + ", ".join(errors))

fixtures = {
    "pending outcome": ("matching marketing and welcome", ""),
    "cross-purpose isolation": ("education permission and receipt remain eligible", ""),
    "acquisition decision": ("`BLOCK: UNVERIFIABLE_ACQUISITION`", ""),
    "lead-magnet decision": ("subscribe only when", ""),
    "unconfirmed contradiction": ("", "\nMark every form submission subscribed."),
    "acquisition contradiction": ("", "\nBought and scraped addresses are permitted."),
    "lead-magnet contradiction": ("", "\nLead-magnet download proves consent."),
}
for label, (deleted_text, appended_text) in fixtures.items():
    mutated = text.replace(deleted_text, "", 1) + appended_text
    if mutated == text:
        raise SystemExit(f"Behavior fixture missing: {label}")
    if not validate(mutated):
        raise SystemExit(f"Behavior fixture accepted: {label}")

print(f"list-growth consent contract OK: {len(trace_requirements)} decision traces; {len(fixtures)} invalid behaviors rejected")
