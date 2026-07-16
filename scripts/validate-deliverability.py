#!/usr/bin/env python3
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
skill = root / "skills" / "21-deliverability-sender-operations" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing deliverability sender-operations skill")

required_contracts = {
    "How": {
        "authentication preflight": ("SPF", "DKIM", "DMARC alignment", "`_dmarc.<domain>` TXT record", "`p=` policy tag"),
        "list hygiene and suppression": ("one-click unsubscribe", "`List-Unsubscribe-Post: List-Unsubscribe=One-Click`", "suppress hard bounces and complaints immediately", "48 hours"),
        "reputation monitoring": ("Postmaster Tools", "0.1%", "0.3%", "never resume full volume immediately"),
        "warm-up and ramping": ("gradual", "most engaged", "45 days", "large, sudden increase"),
        "traffic separation": ("configuration sets", "dedicated IP pools", "never queued behind or throttled"),
    },
    "Do / Don't quick reference": {
        "authenticate": ("SPF and DKIM", "aligned DMARC"),
        "suppress": ("unsubscribes, complaints, and hard bounces", "48 hours"),
        "spam rate": ("0.3%",),
        "ramp": ("Don't resume full sending volume immediately",),
        "separation": ("Don't share transactional and marketing sending infrastructure",),
    },
}

trace_requirements = {
    "Missing DMARC alignment": {
        "given": ("valid SPF and DKIM", "no aligned DMARC"),
        "outcome": ("`HOLD: AUTH_ALIGNMENT_INCOMPLETE`", "publish the `_dmarc` record"),
    },
    "Spam-rate breach": {
        "given": ("0.3%",),
        "outcome": ("`HALT: SPAM_RATE_BREACH`", "reduce volume"),
    },
    "Reputation recovery": {
        "given": ("recovering from a blocklist or throttling incident",),
        "outcome": ("`RECOVER: STAGED_RAMP`", "staged volume ramp", "never at full prior volume immediately"),
    },
    "Unwarmed new IP at full volume": {
        "given": ("newly provisioned dedicated IP", "no sending history", "full target volume on day one"),
        "outcome": ("`BLOCK: WARMUP_REQUIRED`", "gradual warm-up plan"),
    },
    "Suppression sync failure": {
        "given": ("unsubscribed or complained", "still present in an eligible send audience"),
        "outcome": ("`BLOCK: SUPPRESSION_SYNC_FAILURE`", "suppression list is confirmed synchronized"),
    },
    "Never-engaged accumulation": {
        "given": ("not opened or clicked", "no sunset treatment"),
        "outcome": ("`HOLD: LIST_HYGIENE_STALE`", "final re-engagement attempt", "suppress non-responders"),
    },
    "Traffic separation missing": {
        "given": ("share the same sending domain/IP pool", "no configuration-set or pool separation"),
        "outcome": ("`HOLD: TRAFFIC_SEPARATION_MISSING`", "separate the streams"),
    },
    "All gates pass": {
        "given": ("all verified current",),
        "outcome": ("`READY`", "continued monitoring"),
    },
}

contradictions = {
    "immediate full-volume resume": re.compile(r"(?<!never )(?<!don't )(?:always |immediately )resume full (?:sending )?volume immediately after (?:a )?reputation (?:incident|recovery)", re.I),
    "skip authentication": re.compile(r"bulk sending (?:is|remains) fine without (?:SPF|DKIM|DMARC)", re.I),
    "suppression optional": re.compile(r"suppression sync (?:is|remains) optional", re.I),
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
    raise SystemExit("Deliverability contract invalid: " + ", ".join(errors))

fixtures = {
    "auth alignment outcome": ("publish the `_dmarc` record and verify alignment", ""),
    "spam-rate outcome": ("`HALT: SPAM_RATE_BREACH`", ""),
    "recovery ramp outcome": ("never at full prior volume immediately", ""),
    "warmup requirement": ("`BLOCK: WARMUP_REQUIRED`", ""),
    "suppression sync outcome": ("`BLOCK: SUPPRESSION_SYNC_FAILURE`", ""),
    "list hygiene outcome": ("`HOLD: LIST_HYGIENE_STALE`", ""),
    "traffic separation outcome": ("`HOLD: TRAFFIC_SEPARATION_MISSING`", ""),
    "ready outcome": ("`READY`; proceed with the requested sending plan", ""),
    "immediate-resume contradiction": ("", "\nAlways resume full volume immediately after reputation recovery."),
    "skip-auth contradiction": ("", "\nBulk sending is fine without SPF, DKIM, or DMARC."),
    "suppression-optional contradiction": ("", "\nSuppression sync is optional for marketing sends."),
}
for label, (deleted_text, appended_text) in fixtures.items():
    mutated = text.replace(deleted_text, "", 1) + appended_text
    if mutated == text:
        raise SystemExit(f"Behavior fixture missing: {label}")
    if not validate(mutated):
        raise SystemExit(f"Behavior fixture accepted: {label}")

print(f"deliverability sender-operations contract OK: {len(trace_requirements)} decision traces; {len(fixtures)} invalid behaviors rejected")
