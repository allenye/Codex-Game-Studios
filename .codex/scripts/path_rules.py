#!/usr/bin/env python3
"""Route paths to studio Markdown rules. No automatic rule loading is implied."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def expand_braces(pattern):
    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return [pattern]
    return [expanded for part in match[1].split(",")
            for expanded in expand_braces(pattern[:match.start()] + part + pattern[match.end():])]


def glob_regex(pattern):
    """Globstar crosses directories; **/ also matches zero directories."""
    i, out = 0, "^"
    while i < len(pattern):
        if pattern[i:i+3] == "**/":
            out += "(?:.*/)?"
            i += 3
        elif pattern[i:i+2] == "**":
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return out + "$"


def patterns(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        return []
    header = text[4:].split("\n---", 1)[0]
    values = []
    for line in header.splitlines():
        m = re.match(r"\s*-\s+[\"'](.*)[\"']\s*$", line)
        if m:
            values.extend(expand_braces(m[1]))
    return values


def route(path, root=ROOT):
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        relative = candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("Path is outside the project, including symlink targets") from exc
    rules = []
    for rule in sorted((root / ".codex/rules").glob("*.md")):
        if any(re.fullmatch(glob_regex(p), relative) for p in patterns(rule)):
            rules.append(rule.relative_to(root).as_posix())
    return {"path": relative, "rules": rules}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    try:
        print(json.dumps([route(p) for p in args.paths], indent=2))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
