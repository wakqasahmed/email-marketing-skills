#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
skills = plugin.get("skills", [])
missing = [skill for skill in skills if not (root / skill / "SKILL.md").is_file()]
if missing:
    raise SystemExit("Missing plugin skill paths: " + ", ".join(missing))

for skill in skills:
    path = root / skill
    name_line = next(
        (line for line in (path / "SKILL.md").read_text().splitlines() if line.startswith("name: ")),
        None,
    )
    if name_line != f"name: {path.name}":
        raise SystemExit(f"Skill name does not match its directory: {path}")

guardrail_ref = "../00-email-marketing-guardrails/SKILL.md"
missing_ref = [
    skill for skill in skills
    if Path(skill).name != "00-email-marketing-guardrails"
    and guardrail_ref not in (root / skill / "SKILL.md").read_text()
]
if missing_ref:
    raise SystemExit("Campaign skills missing the guardrails dependency: " + ", ".join(missing_ref))

router = root / "skills/18-jurisdiction-compliance-routing/SKILL.md"
if router.is_file():
    router_content = router.read_text()
    required_router_clauses = {
        "fact-first drafting gate": "until all routing facts are complete and the routing result is `SEND`",
        "US route": "**US:**",
        "UK route": "**UK:**",
        "EEA route": "**EEA:**",
        "Canada route": "**Canada:**",
        "unknown-jurisdiction route": "**Unknown or conflicting jurisdiction:**",
        "no universal assertion": "Never describe US, UK, EEA, or Canadian requirements as universally applicable.",
        "HOLD/BLOCK copy prohibition": "Never turn a `HOLD` or `BLOCK` routing result into recipient-facing copy.",
    }
    missing_router_clauses = [
        description for description, clause in required_router_clauses.items() if clause not in router_content
    ]
    if missing_router_clauses:
        raise SystemExit(
            "Jurisdiction router is missing required contract clauses: " + ", ".join(missing_router_clauses)
        )

print(f"validated {len(skills)} plugin skill paths")
