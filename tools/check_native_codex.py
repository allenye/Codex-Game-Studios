#!/usr/bin/env python3
"""Probe actual repository skill discovery through the installed Codex app-server.

No model turn is started. No trust or global setting is changed by this script.
Codex itself may write its normal runtime state. Exit 2 means NOT ASSESSED.
This probe does not certify role spawning, hook execution or model behavior.
"""
import argparse
import json
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args()
    executable = shutil.which("codex")
    if not executable:
        print("NOT ASSESSED: codex is not on PATH")
        return 2
    messages = queue.Queue()
    try:
        process = subprocess.Popen([executable, "app-server", "--stdio", "--strict-config"],
            cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
    except OSError as exc:
        print("NOT ASSESSED: cannot start Codex:", type(exc).__name__)
        return 2

    def read_messages():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass

    # Drain logs without disclosing user config, credentials or transcripts.
    def drain_logs():
        for _ in process.stderr:
            pass

    threading.Thread(target=read_messages, daemon=True).start()
    threading.Thread(target=drain_logs, daemon=True).start()

    def rpc(identifier, method, params):
        process.stdin.write(json.dumps({"id": identifier, "method": method, "params": params}) + "\n")
        process.stdin.flush()
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            try:
                response = messages.get(timeout=min(1, max(0.01, deadline - time.monotonic())))
            except queue.Empty:
                if process.poll() is not None:
                    raise RuntimeError("app-server exited before " + method)
                continue
            if response.get("id") == identifier:
                if "error" in response:
                    raise RuntimeError("app-server rejected " + method)
                return response["result"]
        raise TimeoutError(method)

    try:
        rpc(1, "initialize", {"clientInfo": {"name": "cgs-native-check", "version": "1.0"},
            "capabilities": {"experimentalApi": True}})
        process.stdin.write('{"method":"initialized"}\n')
        process.stdin.flush()
        expected = {p.parent.name for p in (ROOT / ".agents/skills").glob("*/SKILL.md")}
        result = rpc(2, "skills/list", {"cwds": [str(ROOT)], "forceReload": True})
        entries = result.get("data", [])
        found, errors = set(), []
        for entry in entries:
            for skill in entry.get("skills", []):
                path = Path(skill.get("path", "")).resolve()
                if path.is_relative_to(ROOT / ".agents/skills"):
                    found.add(skill["name"])
            for error in entry.get("errors", []):
                path = Path(error.get("path", "")).resolve()
                if path.is_relative_to(ROOT):
                    errors.append(path.relative_to(ROOT).as_posix())
        missing = sorted(expected - found)
        if errors or missing:
            print(json.dumps({"status": "FAIL", "discovered": len(found),
                "missing": missing, "error_paths": errors}, indent=2))
            return 1
        print(json.dumps({"status": "PASS", "layer": "native skill discovery",
            "discovered": len(found), "expected": len(expected)}))
        return 0
    except (OSError, RuntimeError, TimeoutError, KeyError, ValueError) as exc:
        print("NOT ASSESSED:", type(exc).__name__, str(exc))
        return 2
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
