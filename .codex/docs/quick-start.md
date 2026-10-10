# Codex quick start

Read README.md and codex-runtime.md. Start at `$gs-start`; then configure the
engine with `$gs-setup-engine`, write a brief with `$gs-brainstorm`, split it
with `$gs-create-stories`, implement with `$gs-dev-story`, verify with
`$gs-story-done`. The minimal tier remains the default.

Use `$gs-help` to route by project stage and `$gs-settings` to view or adjust
game config. The host's native /help and /settings commands are unrelated.

Roles use TOML under `.codex/agents/` and inherit the session model. Skill
metadata contains name and description; shell checks require actual tool calls.
Read AGENTS.md for rule routing, checkpointing, authorization and evidence.

Native hooks require project and exact-definition trust via /hooks. No copied
Claude status-line or automatic @ imports are assumed. Missing capabilities
and evidence are NOT ASSESSED, not a passing result. See docs/CODEX-VALIDATION.md.
