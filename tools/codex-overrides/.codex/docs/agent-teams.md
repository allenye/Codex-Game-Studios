# Studio teams on Codex

The team workflows use the host's native subagents. They do not depend on
Claude's experimental agent-teams environment variable, shared-task tools,
mailboxes or independent sessions. See coordination-rules.md and codex-runtime.md.

Use only the tools actually exposed by the host; task checkpoints provide a
portable fallback. Run roles sequentially if subagents are unavailable. Always
disclose the execution mode, active roles and unresolved dependencies.
