#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def normalize_plugin_paths(paths: list[str]) -> tuple[list[str], list[str]]:
    names = []
    errors = []
    for raw_path in paths:
        if not isinstance(raw_path, str):
            errors.append(f"plugin skill path is not a string: {raw_path!r}")
            continue
        path = Path(raw_path)
        if path.is_absolute() or len(path.parts) != 2 or path.parts[0] != "skills":
            errors.append(f"invalid plugin skill path: {raw_path}")
            continue
        names.append(path.parts[1])
    return names, errors


def registry_errors(
    actual_names: list[str], plugin_paths: list[str], manifest_names: list[str]
) -> list[str]:
    plugin_names, errors = normalize_plugin_paths(plugin_paths)
    expected = sorted(actual_names)

    duplicate_plugin_names = duplicates(plugin_names)
    if duplicate_plugin_names:
        errors.append("duplicate plugin skills: " + ", ".join(duplicate_plugin_names))

    duplicate_manifest_names = duplicates(manifest_names)
    if duplicate_manifest_names:
        errors.append("duplicate manifest skills: " + ", ".join(duplicate_manifest_names))

    if plugin_names != expected:
        errors.append(f"plugin skills {plugin_names} do not match actual skills {expected}")
    if manifest_names != expected:
        errors.append(f"manifest skills {manifest_names} do not match actual skills {expected}")
    return errors


def validate_registry_mutations(
    actual_names: list[str], plugin_paths: list[str], manifest_names: list[str]
) -> None:
    def renamed(name: str) -> str:
        if name == "18-jurisdiction-compliance-routing":
            return "18-lifecycle-orchestration"
        if name == "19-lifecycle-orchestration":
            return "19-jurisdiction-compliance-routing"
        return name

    renamed_names = [renamed(name) for name in actual_names]
    fixtures = {
        "plugin omission": (plugin_paths[:-1], manifest_names),
        "manifest omission": (plugin_paths, manifest_names[:-1]),
        "plugin duplicate": (plugin_paths + [plugin_paths[-1]], manifest_names),
        "manifest duplicate": (plugin_paths, manifest_names + [manifest_names[-1]]),
        "18/19 rename": ([f"./skills/{name}" for name in renamed_names], renamed_names),
    }
    for label, (mutated_plugin, mutated_manifest) in fixtures.items():
        if not registry_errors(actual_names, mutated_plugin, mutated_manifest):
            raise SystemExit(f"Registry mutation check failed: {label} was accepted")


root = Path(__file__).resolve().parents[1]
plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
skills = plugin.get("skills", [])
manifest = json.loads((root / "manifest.json").read_text())
manifest_skills = manifest.get("skills", [])
actual_skills = sorted(path.parent.name for path in root.glob("skills/*/SKILL.md"))

errors = registry_errors(actual_skills, skills, manifest_skills)
if errors:
    raise SystemExit("Skill registry mismatch: " + "; ".join(errors))
validate_registry_mutations(actual_skills, skills, manifest_skills)

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
        "outbound-Canada routing": "For a Canada-to-non-Canadian recipient group, return `BLOCK`",
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

print(f"validated {len(skills)} plugin skill paths; 5 registry mutations rejected")
