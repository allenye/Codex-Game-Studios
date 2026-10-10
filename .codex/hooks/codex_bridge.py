#!/usr/bin/env python3
"""Adapt Codex lifecycle events to studio checks using only the Python stdlib.

The script never evaluates tool input as code. Hooks are guardrails; sandbox and
host permissions remain the execution boundary. Post-write checks cannot undo
effects. An upstream validation error is returned as native blocking feedback.
"""
import datetime
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUPPORTED = {"SessionStart", "PreToolUse", "PostToolUse", "PreCompact", "PostCompact",
             "Stop", "SessionEnd", "Interrupt", "SubagentStart", "SubagentStop"}


def feedback(event, message, block=False):
    if event == "PreToolUse" and block:
        return {"hookSpecificOutput": {"hookEventName": event,
            "permissionDecision": "deny", "permissionDecisionReason": message}}
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}
    if event == "PostToolUse" and block:
        out.update(decision="block", reason=message)
    return out


def run_check(script, payload, root, timeout=8):
    env = dict(os.environ, CGS_ROOT=str(root))
    try:
        result = subprocess.run(["bash", str(root / ".codex/hooks" / script)],
            input=json.dumps(payload), text=True, capture_output=True, cwd=root,
            env=env, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return "Check unavailable: " + script + " (" + type(exc).__name__ + ")", True
    message = "\n".join(x.strip() for x in (result.stdout, result.stderr) if x.strip())
    return message, result.returncode != 0


def command_text(tool_input):
    command = tool_input.get("command", tool_input.get("cmd"))
    if isinstance(command, list) and all(isinstance(x, str) for x in command):
        return shlex.join(command)
    if not isinstance(command, str):
        raise ValueError("Shell event has no valid command string")
    return command


def destructive_command(command):
    # Inspect tokens, not arbitrary text in quoted commit messages. This catches
    # common chained/global-option forms; it is intentionally not a shell parser
    # or a substitute for native permissions and sandboxing.
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace_split = True
    lexer.commenters = "#"
    try:
        tokens = list(lexer)
    except ValueError:
        return "Cannot parse shell command for studio policy"
    starts = [0] + [i+1 for i, t in enumerate(tokens) if t in (";", "&&", "||", "|", "&", "(", ")")]
    # shlex treats newlines as whitespace; include each line's first command.
    if "\n" in command:
        for line in command.splitlines():
            reason = destructive_command(line)
            if reason:
                return reason
    for start in starts:
        words = tokens[start:]
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            words = words[1:]
        if not words:
            continue
        executable = Path(words[0]).name
        if executable == "sudo":
            return "Studio policy disallows privilege escalation"
        if executable in ("bash", "sh", "zsh") and "-c" in words:
            idx = words.index("-c")
            if idx+1 < len(words):
                reason = destructive_command(words[idx+1])
                if reason:
                    return reason
        if executable == "rm":
            flags = [w for w in words[1:] if w.startswith("-")]
            recursive = any(w == "--recursive" or (not w.startswith("--") and any(c in w for c in "rR")) for w in flags)
            force = any(w == "--force" or (not w.startswith("--") and "f" in w) for w in flags)
            if recursive and force:
                return "Studio policy blocks recursive forced deletion"
        if executable not in ("git", "git.exe"):
            continue
        i = 1
        while i < len(words) and words[i].startswith("-"):
            i += 2 if words[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
        if i >= len(words):
            continue
        operation, args = words[i], words[i+1:]
        if operation == "push" and any(a.startswith("--force") or a.startswith("+") or (a.startswith("-") and not a.startswith("--") and "f" in a) for a in args):
            return "Studio policy blocks forced Git pushes"
        if operation == "reset" and "--hard" in args:
            return "Studio policy blocks hard Git reset"
        if operation == "clean" and any(a == "--force" or (a.startswith("-") and not a.startswith("--") and "f" in a) for a in args):
            return "Studio policy blocks forced Git clean"
    return ""


def patch_paths(tool_input):
    command = tool_input.get("command", tool_input.get("patch", tool_input.get("input", "")))
    if not isinstance(command, str):
        raise ValueError("Patch event has no valid patch string")
    return [m[1].strip() for m in re.finditer(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", command, re.M)]


def inside(path, root):
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    candidate.relative_to(root.resolve())
    return candidate


def changed_paths(tool, inputs, root):
    if tool == "apply_patch":
        return patch_paths(inputs)
    if inputs.get("file_path"):
        return [inputs["file_path"]]
    if tool in ("Bash", "exec_command"):
        result = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"],
            cwd=root, text=True, capture_output=True, timeout=5)
        if result.returncode:
            return []
        values, paths, i = result.stdout.split("\0"), [], 0
        while i < len(values):
            item = values[i]
            if item:
                paths.append(item[3:])
                if "R" in item[:2] or "C" in item[:2]:
                    i += 1
            i += 1
        return paths
    return []


def handle(payload, root=ROOT):
    root = root.resolve()
    event = payload.get("hook_event_name", "")
    if event not in SUPPORTED:
        return {"systemMessage": "Unsupported studio event: " + str(event)}, 0
    inputs = payload.get("tool_input") or {}
    if not isinstance(inputs, dict):
        return feedback(event, "Malformed tool_input", block=True), 2 if event == "PreToolUse" else 0
    tool = payload.get("tool_name", "")
    cwd = Path(payload.get("cwd", str(root))).resolve()
    try:
        cwd.relative_to(root.resolve())
    except ValueError:
        return feedback(event, "Event cwd is outside this studio project", True), 2 if event == "PreToolUse" else 0
    if event == "PreToolUse":
        if tool in ("Bash", "exec_command"):
            try:
                command = command_text(inputs)
            except ValueError as exc:
                return feedback(event, str(exc), True), 2
            reason = destructive_command(command)
            if reason:
                return feedback(event, reason, True), 2
            normalized = dict(payload, tool_input=dict(inputs, command=command))
            messages = []
            for script in ("validate-commit.sh", "validate-push.sh"):
                message, failed = run_check(script, normalized, root)
                if message:
                    messages.append(message)
                if failed:
                    return feedback(event, "\n".join(messages), True), 2
            return feedback(event, "\n".join(messages)) if messages else {}, 0
        if tool in ("apply_patch", "Write", "Edit"):
            paths = patch_paths(inputs) if tool == "apply_patch" else [inputs.get("file_path", "")]
            for path in paths:
                try:
                    target = inside(cwd / path, root)
                except ValueError:
                    return feedback(event, "Patch path escapes the studio project", True), 2
                if any(part.startswith(".env") for part in target.relative_to(root).parts):
                    return feedback(event, "Studio policy blocks editing environment secrets", True), 2
        return {}, 0
    if event == "PostToolUse":
        messages, failed = [], False
        for path in changed_paths(tool, inputs, root):
            try:
                base = root if tool in ("Bash", "exec_command") else cwd
                target = inside(base / path, root)
            except ValueError:
                continue
            relative = target.relative_to(root).as_posix()
            if not target.is_file():
                continue
            if relative.startswith(("assets/", "Assets/", "Content/")) and target.suffix.lower() == ".json":
                try:
                    json.loads(target.read_text())
                except (ValueError, OSError) as exc:
                    messages.append("Invalid asset JSON: " + relative + " (" + type(exc).__name__ + ")")
                    failed = True
            if relative.startswith(".agents/skills/"):
                messages.append("Skill changed: run tools/validate_codex.py and its behavioral spec")
        return feedback(event, "\n".join(dict.fromkeys(messages)), failed) if messages else {}, 0
    if event == "SessionStart":
        messages = []
        for script in ("session-start.sh", "detect-gaps.sh"):
            message, failed = run_check(script, payload, root)
            if message:
                messages.append(message)
            if failed:
                messages.append("NOT ASSESSED: " + script)
        return feedback(event, "\n".join(messages)[:12000]), 0
    checkpoint = root / "production/session-state/active.md"
    if event in ("PreCompact", "PostCompact", "Stop", "Interrupt"):
        # No deletion or rotation per response: preserve resumable task state.
        return feedback(event, "Keep the task checkpoint at production/session-state/active.md; read it after resume/compaction."), 0
    if event in ("SubagentStart", "SubagentStop", "SessionEnd"):
        # Lifecycle audit is opt-out using the same config resolver as workflows.
        result = subprocess.run(["bash", "-c", 'source .codex/hooks/yaml-helper.sh; session_state_enabled'],
            cwd=root, capture_output=True, timeout=1 if event == "SessionEnd" else 5)
        if result.returncode == 0:
            folder = root / "production/session-logs"
            inside(folder, root)
            folder.mkdir(parents=True, exist_ok=True)
            record = {"event": event, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "session_id": str(payload.get("session_id", "unknown"))[:128],
                "agent_id": str(payload.get("agent_id", ""))[:128],
                "agent_type": str(payload.get("agent_type", ""))[:128]}
            log = inside(folder / "codex-lifecycle.jsonl", root)
            with log.open("a") as stream:
                stream.write(json.dumps(record) + "\n")
        return {}, 0
    return {}, 0


def main():
    expected = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("Event must be an object")
        if expected and payload.get("hook_event_name") != expected:
            raise ValueError("Event does not match registered handler")
        result, code = handle(payload)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        message = "Studio hook failed: " + type(exc).__name__ + ": " + str(exc)
        code = 2 if expected == "PreToolUse" else 0
        result = feedback(expected, message, True) if code else {"systemMessage": message}
    if result:
        print(json.dumps(result))
    if code == 2:
        print(result.get("hookSpecificOutput", {}).get("permissionDecisionReason", "Studio check denied operation"), file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
