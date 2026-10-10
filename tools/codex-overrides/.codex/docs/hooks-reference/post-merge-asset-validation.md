# Codex hook contract

Native registrations are in `.codex/hooks.json`; the implementation is
`.codex/hooks/codex_bridge.py`. Read both before trusting the hooks.

- Every event receives a JSON object with hook_event_name, cwd and session_id.
- Bash/exec_command inputs normalize command or cmd; apply_patch provides the
  patch through tool_input.command. File paths resolve from event cwd.
- PreToolUse returns a native permissionDecision deny and exit 2 for a failed
  check. Informational output uses hookSpecificOutput.additionalContext.
- PostToolUse returns blocking feedback on invalid asset JSON. The write already
  happened: the hook reports it for repair and cannot undo it.
- SessionStart loads checked project context; Stop preserves active.md.
- Subagent events append bounded metadata. They never dump command contents
  or full transcripts. features.session_state controls lifecycle auditing.
- Notification and the Claude status-line integration have no port registration.
- Project and exact hook trust are required. New or changed hashes require review.

The bridge is a guardrail, not a security boundary. Uncovered tools and untrusted
hooks require manual checks. See docs/CODEX-VALIDATION.md for tested coverage.

Official contract: https://learn.chatgpt.com/docs/hooks
