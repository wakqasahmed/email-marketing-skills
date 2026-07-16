#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = root / "skills" / "18-lifecycle-orchestration" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing lifecycle orchestration skill")

text = skill.read_text()
required_contract = {
    "contact-level decision": "## Contact-level decision order",
    "event precedence": "## Event precedence and ownership",
    "global and segment caps": "global and every applicable segment cap",
    "quiet periods": "quiet period",
    "channel preferences": "channel preference",
    "deduplication": "deduplication key",
    "recent-purchase suppression": "recent-purchase suppression",
    "experiment holdouts": "holdout assignment",
    "campaign calendar": "Campaign calendar",
    "monitoring": "Monitoring and exception report",
    "service priority": "essential service messages bypass marketing scheduling",
    "anti-bypass": "must never carry marketing content or reset, evade, or consume marketing caps",
}

missing = [label for label, phrase in required_contract.items() if phrase not in text]
if missing:
    raise SystemExit("Lifecycle orchestration contract missing: " + ", ".join(missing))

print("lifecycle orchestration contract OK")
