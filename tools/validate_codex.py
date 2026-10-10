#!/usr/bin/env python3
"""Offline structural validation; does not certify model behavior or gameplay."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from port_to_codex import build, frontmatter

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT, reproducible=True):
    errors = []
    manifest = json.loads((root / ".codex/port-manifest.json").read_text())
    skills = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    agents = sorted((root / ".codex/agents").glob("*.toml"))
    upstream_skills = list((root / ".claude/skills").glob("*/SKILL.md"))
    upstream_agents = list((root / ".claude/agents").glob("*.md"))
    if len(skills) != len(upstream_skills) or len(skills) != len(manifest["skills"]):
        errors.append("Skill coverage differs from upstream/manifest")
    if len(agents) != len(upstream_agents) or len(agents) != len(manifest["agents"]):
        errors.append("Role coverage differs from upstream/manifest")
    names = set()
    for p in skills:
        try:
            meta, body = frontmatter(p.read_text())
            if set(meta) != {"name", "description"} or not meta.get("description"):
                errors.append(f"Invalid native metadata: {p.relative_to(root)}")
            name = meta.get("name", "")
            if name != p.parent.name or not re.fullmatch(r"gs-[a-z0-9-]{1,60}", name) or name in names:
                errors.append("Invalid/duplicate skill name: " + name)
            names.add(name)
            if not (p.parent / "references/workflow.md").is_file():
                errors.append("Missing workflow: " + name)
            for ref in p.parent.rglob("*.md"):
                text = ref.read_text()
                if re.search(r"^!`|CLAUDE_SKILL_DIR|CLAUDE_PROJECT_DIR|\bAskUserQuestion\b|\bTaskCreate\b", text, re.M):
                    errors.append("Unported mechanics: " + str(ref.relative_to(root)))
                # Literal reference paths are resolved from the skill folder,
                # matching the adapter's documented reference-base convention.
                for path in re.findall(r"`(references/[^`\s<>\[\]*]+\.md)`", text):
                    if not (p.parent / path).is_file():
                        errors.append(f"Missing skill reference: {name}: {path}")
        except (ValueError, OSError) as exc:
            errors.append(f"Unreadable skill {p.name}: {exc}")
    for p in agents:
        try:
            role = tomllib.loads(p.read_text())
            if not all(isinstance(role.get(k), str) and role[k] for k in ("name", "description", "developer_instructions")):
                errors.append("Incomplete role: " + p.name)
            if role.get("name") != p.stem:
                errors.append("Role name/path mismatch: " + p.name)
            if set(role) - {"name", "description", "developer_instructions", "sandbox_mode"}:
                errors.append("Unexpected role override: " + p.name)
            if role.get("sandbox_mode", "read-only") != "read-only":
                errors.append("Unexpected role permission expansion: " + p.name)
        except (ValueError, OSError) as exc:
            errors.append(f"Unparseable role {p.name}: {exc}")
    try:
        tomllib.loads((root / ".codex/config.toml").read_text())
    except ValueError as exc:
        errors.append("Invalid project config: " + str(exc))
    native = json.loads((root / ".codex/hooks.json").read_text())
    supported = {"SessionStart", "PreToolUse", "PostToolUse", "PreCompact", "PostCompact",
                 "Stop", "SubagentStart", "SubagentStop", "SessionEnd", "Interrupt"}
    if set(native["hooks"]) != supported:
        errors.append("Native lifecycle event coverage mismatch")
    for event, groups in native["hooks"].items():
        for group in groups:
            for handler in group["hooks"]:
                command = handler.get("command", "")
                if handler.get("type") != "command" or "codex_bridge.py" not in command or not command.endswith(" " + event):
                    errors.append("Invalid hook bridge registration: " + event)
                if "CLAUDE" in command or "dangerously" in command:
                    errors.append("Unsafe/obsolete hook command: " + event)
    for item in manifest["resources"]:
        p = root / item["source"]
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item["source_sha256"]:
            errors.append("Source changed without regeneration: " + item["source"])
    if reproducible:
        for path, content in build().items():
            p = root / path
            if not p.is_file() or p.read_text() != content:
                errors.append("Generated drift: " + path)
    for p in sorted((root / ".codex").rglob("*.sh")):
        result = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
        if result.returncode:
            errors.append("Invalid shell syntax: " + p.relative_to(root).as_posix())
    # Fail on broken literal root references, excluding documented placeholders,
    # wildcards, commands and dynamically created runtime artifacts.
    for p in list((root / ".agents/skills").rglob("*.md")) + list((root / ".codex/docs").rglob("*.md")):
        for target in re.findall(r"`((?:\.codex|\.agents)/[^`\s<>\[\]*{}]+\.(?:md|sh|py|toml|yaml))`", p.read_text()):
            if target.startswith(".codex/agent-memory/"):
                continue
            if not (root / target).is_file():
                errors.append(f"Broken root reference: {p.relative_to(root)} → {target}")
    return {"status": "FAIL" if errors else "PASS", "skills": len(skills),
            "roles": len(agents), "generated_files": len(manifest["generated_files"]),
            "errors": sorted(set(errors)), "scope": "offline structural validation only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2) if args.json else f"{result['status']}: {result['skills']} skills, {result['roles']} roles; {len(result['errors'])} defects\n" + "\n".join(result["errors"]))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
