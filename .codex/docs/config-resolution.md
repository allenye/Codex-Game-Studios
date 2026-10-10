# Config resolution on Codex

Use an explicit shell tool call; Codex does not run Markdown preprocessing or
honor Claude allowed-tools grants. Locate the root from the skill path, then
set CGS_ROOT to that absolute path in the same shell invocation:

```bash
bash "$CGS_ROOT/.codex/hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow
```

Check the actual output and provenance. Pass a system name for per-system
resolution. If the helper fails or is unavailable, report NOT ASSESSED instead
of pretending a config block was injected. The helper finds its own root and
preserves upstream resolution order and enum fallback behavior.

## Resolution chain

| Step | Source | Applies to |
|---|---|---|
| 1 | `project.local.yaml` | any setting on the `$gs-settings --local` whitelist (12 keys — `modes.review_mode`, `modes.automation`, `modes.automation_always_ask`, `team.size`, all five `testing.strict.*`, `performance.enforce`, `features.*`) |
| 2 | `project.yaml` | all keys |
| 3 | legacy plain-text mirror | `modes.review_mode` → `production/review-mode.txt`; `project.stage` → `production/stage.txt` |
| 4 | **`modes.rigor` expansion** | the six knobs `rigor` fronts — `modes.workflow`, `docs.density`, `qa.level`, `modes.story_granularity`, `modes.review_mode`, `team.size` |
| 5 | documented default | the table below |

An **enum-invalid value does not win** — the chain continues past it and the
rejected value is named on the `notes:` line. A typo degrades to the documented
default rather than propagating a nonsense mode into every skill.

> **Step 4 sits below every explicit source and above the terminal default, and
> that ordering is the whole back-compat guarantee.** A `project.yaml` that
> already sets `docs.density: terse` resolves exactly as it did before `rigor`
> existed, because step 2 answers first. Invert steps 4 and 5 and `rigor` becomes
> a no-op; hoist step 4 above step 2 and it silently overrides settings people
> already have.
>
> Derived values report their provenance as **`rigor:<level>`**, so the source
> vocabulary is `{project.local.yaml, project.yaml, <legacy path>, rigor:<level>,
> default, unset}`. `docs.density: balanced (rigor:standard)` says the value was
> never written down anywhere — it follows the project's rigor level and will
> move if that level moves.

> **Read scope == write whitelist.** Anything `$gs-settings --local` may *write*
> is also *read* during resolution. If the read scope were ever narrower,
> `$gs-settings --local modes.review_mode=solo` would write a value
> that `$gs-settings` accepted and displayed and every skill then ignored. The
> test suite asserts the two lists stay in step — adding a setting to one
> without the other reproduces that bug.
>
> This matches the spec: `effects-map.md` § "Local Override Pattern" has always
> stated the chain applies to *every* setting. The narrow read scope was an
> implementation gap, not a design.

> **A key OUTSIDE the whitelist, hand-written into `project.local.yaml`, is
> reported rather than swallowed.** `$gs-settings --local` refuses to
> write one, but the file exists to be edited by hand, so that path needs its own
> guard. `modes.rigor: full` written there is a real key with a legal value, so
> `validate_yaml_enum` passes it — and then resolution never consults the local
> file for that path, so the setting vanishes and the user sees the default they
> were trying to override, with no error anywhere. Every check in the chain
> validated the **value**; nothing validated the **location**.
>
> `validate_local_scope` now names such keys on `notes:`. It **warns and never
> reconciles**, the same shape as the stage-mirror check: it does not edit the
> file, does not begin honouring the key, and does not change resolution. A
> locked setting is locked because it decides which artifacts exist on disk, so
> a helper that quietly applied one would let two developers' checkouts diverge
> — the exact thing the whitelist prevents. The user moves the key to
> `project.yaml` or deletes it.
>
> `schema_version` and `framework.*` are exempt: `effects-map.md` classes them as
> file metadata rather than preferences, and a `project.local.yaml` carrying
> `schema_version: 1` is correct as written.

## Defaults

| Knob | Default |
|---|---|
| `modes.automation` | `collaborative` |
| `modes.rigor` | `minimal` |
| `modes.automation_always_ask` | `scope_changes`, `file_deletions`, `schema_changes` |

**The six knobs `rigor` fronts have no terminal default at all.** `modes.workflow`,
`docs.density`, `qa.level`, `modes.story_granularity`, `modes.review_mode` and `team.size` are
deliberately absent from `_yaml_helper_defaults`: a default there would answer at step 5 before the
expansion at step 4 ever ran, making `rigor` a no-op for anyone who had not also
set the sub-knob. Their effective values come from the rigor level:

| `modes.rigor` | `modes.workflow` | `docs.density` | `qa.level` | `modes.story_granularity` | `modes.review_mode` | `team.size` |
|---|---|---|---|---|---|---|
| `minimal` (default) | `minimal` | `terse` | `minimal` | `coarse` | `solo` | `individual` |
| `standard` | `standard` | `balanced` | `standard` | `balanced` | `lean` | `individual` |
| `full` | `full` | `thorough` | `full` | `fine` | `full` | `studio` |

Because `rigor` itself defaults to `minimal`, an unconfigured project resolves
these six to the lean row. That default was `standard`; it changed because the
heavier tier costs more to reach working code without producing a better
result. See the rationale block above `_yaml_helper_defaults`
in `.codex/hooks/yaml-helper.sh` for the reasoning and the ordering
constraint. Raising the tier is one question in `$gs-start` or one `$gs-settings`
call, and `settings-guidance.md § 4`'s upward triggers are written to fire from
this starting state. (`team.size` is the one knob the flip does not move:
`minimal` and `standard` both yield `individual`, and only `full` opts into the
`studio` roster.)

> **The flip DOES reach existing projects.** A `project.yaml` that sets some of
> the six explicitly but never sets `rigor` keeps its explicit values and takes
> the new `minimal` row for the rest -- so an unset `qa.level` that used to
> resolve `standard` now resolves `minimal`.
> Pin the old behaviour by setting `modes.rigor: standard` explicitly; see
> UPGRADING.md.

`modes.workflow` is **fronted, not replaced**: it keeps
`workflow_overrides.system_overrides`, which still beats the derived value.
Setting any of the six explicitly overrides just that one and leaves
its siblings on the rigor level, which is how "comprehensive but compact"
(`rigor: full` + `docs.density: terse`) stays expressible. Two of the six —
`modes.review_mode` and `team.size` — are personal-experience knobs that also
remain overridable from `project.local.yaml` (that source sits above the
expansion), unlike the four on-disk knobs, which are locked.

> **Keep this table in step with the helper.** Every knob listed here must carry
> the value `_yaml_helper_defaults` returns (read it through `get_yaml_default`),
> and none of the six fronted knobs may appear in it.

**`testing.strict.*` has no central default on purpose.** Its unset default
differs per skill by design: `$gs-smoke-check` treats unset as **blocking** (it is a
build-health gate), while `$gs-story-done` and `$gs-dev-story` apply the per-story-type
table in `.codex/docs/coding-standards.md`. `resolve_config` therefore reports
only the *configured state* (`unset` where absent) and each skill applies its own
default. The script resolves **sources**; the skill owns **policy**.

**`engine` is reported from `project.yaml` only.** No markdown reader is built.
Skills keep their existing per-field fallback to
`.codex/docs/technical-preferences.md`, which also remains the sole source for
forbidden patterns and allowed libraries — those never migrated.

## Failure modes

`resolve_config` **always exits 0 and always emits a complete block.** Each
condition below degrades to defaults and is named on `notes:`:

| Condition | Behavior |
|---|---|
| `project.yaml` absent | legacy → defaults; `notes: project.yaml absent` |
| `project.yaml` **empty** | defaults; `notes: project.yaml is EMPTY`. Distinct from absent on purpose — a truncated write or an interrupted `$gs-setup-engine` looks like this |
| Malformed YAML | unparseable keys resolve empty and fall through |
| Tab-indented lines | rejected, and the **line numbers are named** on `notes:` |
| CRLF line endings | parsed correctly (the Windows default) |
| UTF-8 BOM | parsed correctly; the BOM does not poison the first key |
| 3-space indent | parsed correctly; the parser is indent-tolerant |
| Key present, value empty | treated as **unset**; falls through to the next source, never to `""` |
| Enum-invalid value | chain continues; rejected value named in `notes:` |
| `project.local.yaml` without a base | `validate_local_yaml_base` message on `notes:` |
| Locked key in `project.local.yaml` | ignored as always, but now **named** on `notes:` — `local: not locally overridable, ignored — modes.rigor (move to project.yaml or delete)` |
| No Python interpreter | legacy files and defaults only; **explicitly noted** on `notes:` |
| No block at all | shell preprocessing disabled (`disableSkillShellExecution`) — use the defaults table above |
| A task notice where the block should be ("Command did not complete within its 120s timeout and was moved to the background") | the settings line ran past Codex's 120-second limit for a skill's `!` line, because every process start was slowed — usually by antivirus real-time scanning of the project folder. The settings exist: read each key yourself from `project.local.yaml`, then `project.yaml`, then the defaults table above |
| Bootstrap line not approved, or exits non-zero | **not a degraded state — the skill never renders at all.** See "Why exactly this command" above |

A skill must never treat a missing block as "config is unset in an interesting
way". It means the block did not render; the defaults apply. The exception is
that task notice: the settings line ran out of time, not the settings, so read
the files as that row says instead of taking the defaults. If it keeps
happening, exclude the project folder from real-time scanning.

### Two inputs that resolve without a note

In both cases `resolve_config` follows a fixed rule and emits no note, so it does
not tell you that something you wrote was not used.

| Input | What happens | Note emitted |
|---|---|---|
| **Duplicate key** (`rigor:` twice in one block) | **the last occurrence wins**, deterministically | **none** |
| **Wrong shape** — a list where a scalar belongs (`rigor:` followed by `- standard`) | key resolves empty, falls through to the default | **none** |

An enum-*invalid* value is announced (`modes.workflow: 'medium' is not a valid
value … — ignored, chain continued`). A wrong shape is not: the key is present
but resolves to nothing, which is also what a key with an empty value does on
purpose (the "Key present, value empty" row above), and `resolve_config` does not
tell the two apart. When a setting seems ignored, check the structure of its key
in the file: one scalar on the key's own line, the key written once per block,
and no list under it. `$gs-settings` shows the value that is actually in effect.

The last-wins rule for a duplicate key is fixed, so you can rely on it.

## Why not inject at session start

`resolve_config` is also safe to call from a hook, but session-start does **not**
call it. The block would cost tokens on every session whether or not any skill
needs config, and it would go stale mid-session as `$gs-settings` writes land. The
per-skill body call is fresher and only loads where it is used. Session start
still prints the resolved review mode and any schema errors, which is the part a
human reads.

## Testing

The resolution chain, the legacy reader, enum fall-through, block shape and
every failure mode above are covered by the framework's own test suite under
`tests/`, along with the `modes.rigor` expansion and its precedence in both
directions. Two properties are asserted that are easy to lose:

- The local **read** scope and the `$gs-settings --local` **write** whitelist stay
  in step. If they drift, `$gs-settings` accepts and displays a value that every
  skill then ignores.
- The expansion is *reachable* (`$gs-start` asks about it) and *legible*
  (`$gs-settings` reports derived values rather than "(not set)"). A correct
  expansion nobody is asked about and no view displays would be worth nothing.
