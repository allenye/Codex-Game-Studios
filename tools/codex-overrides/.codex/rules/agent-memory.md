---
paths:
  - ".codex/agent-memory/**"
  - "production/session-state/**"
---

# Task memory

Keep concise file-backed checkpoints and role notes inside the authorized task.
Do not store secrets, entire transcripts or unrelated user data. These runtime
paths are gitignored. Preserve pending decisions and unresolved blockers; a
compaction, timeout or assistant reply is not evidence that a task finished.

Follow codex-runtime.md authorization semantics. Do not use a memory file as
permission to change unrelated source, publish externally or broaden scope.
