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

print(f"validated {len(skills)} plugin skill paths")
