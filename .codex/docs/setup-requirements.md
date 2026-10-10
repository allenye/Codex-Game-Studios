# Codex setup

Required for this port: Python 3.11+, Git, Bash (Git Bash on Windows), a Codex
client supporting repository skills and custom agents. The local client inspected
for this port is codex-cli 0.162.0-alpha.2. Its schema and execution-policy parser
were checked; native startup was blocked by the host sandbox. No client version
is certified for full end-to-end operation by the offline checks.
No third-party Python packages are required for port checks. Game development
also requires the chosen engine and its build/test tools.

Clone the fork, start Codex at its root, then invoke `$gs-start`. The model and
account authentication are configured by the user; no install script edits
global configuration or copies credentials. For nested directories, repository
skills and AGENTS.md still apply. Helpers resolve their root explicitly.

Trust the project `.codex/` layer through the client's normal review flow.
Review `.codex/hooks.json` and its bridge and scripts, then use `/hooks` to trust
the exact definitions. New definitions need review again. Until trust is granted,
hooks can be skipped: run `tools/validate_codex.py` and required checks manually.
This port does not automatically trust hooks or bypass approvals and sandboxing.

Use `.codex/docs/config-resolution.md` for game settings. Host approval and
sandbox settings remain separate from `modes.automation`. Project-local TOML
does not grant permission to publish or perform destructive actions.

Port checks:
```bash
python3 tools/port_to_codex.py --check
python3 tools/validate_codex.py
python3 -m unittest discover -s tests/codex_port -v
```

See docs/CODEX-VALIDATION.md for actual tested behavior and remaining limits.
