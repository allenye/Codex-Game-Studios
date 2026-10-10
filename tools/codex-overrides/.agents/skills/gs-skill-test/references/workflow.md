# Studio skill and role tests

Arguments: `static [name|all]`, `spec [name]`, `category [name|all]`, `audit`.
Normalize original names to gs- names for skills; role names are unchanged.

## 1. Structural checks

Run `python3 tools/validate_codex.py` at the project root. It checks native
frontmatter/TOML, coverage, source hashes, generated drift, literal references,
hook registrations and script syntax. For a single name, additionally inspect
that skill and its references or role instructions. Only name and description
are required in skill frontmatter. Claude allowed-tools/model/context fields
and mandatory phase counts are not native requirements.

## 2. Behavioral checks

Read `.codex/testing/catalog.yaml` and use the entry's spec and category paths;
do not guess paths. Read the full selected native skill and needed references,
or role TOML, then AGENTS.md and codex-runtime.md. Port-specific runtime rules
take precedence over upstream spec assertions about tools, model labels,
automatic imports or repeated file approvals. Mark those assertions SUPERSEDED
with the actual replacement behavior; do not count them as an executed PASS.

Test genuine workflow outcomes, using isolated fixtures. Check tool calls,
artifacts and diffs rather than self-reported completion. Missing capabilities
produce NOT ASSESSED. Do not run external mutations during tests without scope.

## 3. Category and audit

Apply the relevant quality rubric to preserved game semantics. For an audit,
compare the actual 74 skill/49 role inventory with the manifest and catalog.
List coverage denominators, executed cases, failures and unassessed cases.
Structural checks and unexecuted specs are separate evidence levels.

## 4. Failure and optimization

Record a reproducible failure with input, expected behavior, actual tool evidence
and severity. Add the counterexample as a regression test before fixing its
cause. Retest the failed case and related cases, then the required suite.
Use `$gs-skill-improve` for an authorized test/fix/retest cycle. Save a report
only within the user's authorized destination; otherwise report in chat.
