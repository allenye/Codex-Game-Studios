# Codex Game Studios

A Codex-native game development studio template adapted from
[Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios),
upstream version 1.1.3 at `be8993bbc5a1f016bc770b2846ce06272d284526`.

**74 repository skills, 49 native custom roles, preserved game workflows and
10 native lifecycle event registrations.** Godot, Unity and Unreal design,
programming, QA and production guidance are retained. This is a workflow template,
not an engine, a shipped game or a guarantee of finished art/audio.

[中文说明](README.zh-CN.md) · [Migration plan](docs/CODEX-MIGRATION-PLAN.md) ·
[Validation evidence and limits](docs/CODEX-VALIDATION.md)

## Start

Requirements: Python 3.11+, Git, Bash (Git Bash on Windows), a compatible Codex
client, and the chosen game engine. Native client compatibility is recorded in
the validation report; earlier clients have not been certified by this fork.

```bash
git clone --branch codex-port https://github.com/allenye/Codex-Game-Studios.git my-game
cd my-game
python3 tools/validate_codex.py
codex
```

In Codex, invoke `$gs-start` or describe your goal. Repository skills are
discovered in `.agents/skills/`; the `gs-` prefix avoids collisions with native
commands such as `/help` and `/settings`.

Review the project `.codex/` layer through the normal client trust flow. Inspect
`.codex/hooks.json`, its Python bridge and invoked scripts, then use `/hooks` to
review and trust the exact hook definitions. Until that happens, hooks may be
skipped: do not assume checks have run. No setup script changes global trust,
credentials, model choice or sandbox settings.

## Typical workflows

| Goal | Skills |
| --- | --- |
| Start a project | `$gs-start`, `$gs-setup-engine`, `$gs-brainstorm` |
| Get to playable code | `$gs-create-stories`, `$gs-dev-story`, `$gs-story-done` |
| Design and architecture | `$gs-map-systems`, `$gs-design-system`, `$gs-create-architecture` |
| Inspect or change game settings | `$gs-settings modes.rigor`, `$gs-settings modes.rigor=standard` |
| Review and validate | `$gs-code-review`, `$gs-smoke-check`, `$gs-gate-check` |
| Coordinate a feature | `$gs-team-combat`, `$gs-team-ui`, `$gs-team-qa` |
| Discover next steps | `$gs-help` |

`project.yaml` remains the game config. The default `minimal` rigor targets a
small playable prototype; `standard` and `full` add process. `project.local.yaml`
is a gitignored personal override. Existing user decisions and authorization
carry across phases; missing required answers never become assumed consent.

## What is native, and what is adapted

- `AGENTS.md` is the project entrypoint; it explicitly routes to relevant docs.
- `.agents/skills/gs-*/SKILL.md` holds native name/description metadata and loads
  full workflows and phase references on demand. Shell helpers run via real
  tool calls, not Claude Markdown preprocessing.
- `.codex/agents/*.toml` defines the 49 roles. Models inherit the session;
  Claude aliases, tool allowlists and maxTurns are provenance only.
- `.codex/hooks.json` registers a stdlib Python bridge for Codex event payloads,
  patch asset validation, commit checks and checkpoint/lifecycle handling.
- `.codex/rules/*.md` are explicitly routed by `path_rules.py` before edits;
  these are not automatically loaded Claude path rules. The separate
  `studio.rules` provides native partial execpolicy guardrails.
- `.claude/`, `CLAUDE.md` and `CCGS Skill Testing Framework/` are preserved
  upstream sources. Codex uses the migrated layer, not those configurations.

See [.codex/docs/codex-runtime.md](.codex/docs/codex-runtime.md) for operation
mappings, sequential fallback, authorization and honest evidence requirements.
Hooks and instructions are guardrails; the sandbox and host policy remain the
execution boundary. Missing engines, tools or real visual evidence must produce
NOT ASSESSED rather than a fabricated PASS. GUI workflows need actual engine
launches, observations and screenshots; generated images are not run evidence.

## Verify and maintain

```bash
python3 tools/port_to_codex.py --check
python3 tools/validate_codex.py
python3 -m unittest discover -s tests/codex_port -v
codex execpolicy check --rules .codex/rules/studio.rules -- git push --force origin main
```

The generator and `.codex/port-manifest.json` retain coverage and source hashes.
Make semantic changes in `tools/codex-overrides/`, regenerate, then test. Runtime
adapters, AGENTS.md and the native config are hand-authored. CI runs offline
structural and adversarial tests; model-based and engine tests are reported
separately and are never implied by a green static check.

When verification fails: reproduce the input, add a regression case, fix the
cause, rerun the case and related checks. Do not erase failures or weaken the
criterion to produce a PASS. `$gs-skill-test` and `$gs-skill-improve` support
these steps and distinguish superseded upstream assertions from actual defects.

## Attribution and license

MIT. The original [LICENSE](LICENSE), upstream authorship and Git history are
preserved. This fork's Codex adaptation does not imply upstream or OpenAI
endorsement. Upstream funding links continue to support the original project.
