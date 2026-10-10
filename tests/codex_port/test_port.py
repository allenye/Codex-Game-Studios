import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


bridge = module("bridge", ROOT / ".codex/hooks/codex_bridge.py")
rules = module("path_rules", ROOT / ".codex/scripts/path_rules.py")
sys.path.insert(0, str(ROOT / "tools"))
import port_to_codex
import validate_codex


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="studio with spaces ")
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / ".codex/hooks", self.root / ".codex/hooks")
        (self.root / "project.yaml").write_text("modes:\n  rigor: minimal\nengine:\n  name: Godot\n")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def event(self, event, tool="", inputs=None, cwd=None):
        return bridge.handle({"hook_event_name": event, "tool_name": tool,
            "tool_input": inputs or {}, "cwd": str(cwd or self.root), "session_id": "test"}, self.root)

    def test_destructive_commands_are_blocked_without_execution(self):
        cases = ["git push --force origin main", "git -C 'path with spaces' push origin +main",
            "git status && git reset --hard HEAD", "git clean -qdf", "rm -r -f build",
            "rm --recursive --force build", "GIT_DIR=.git git push -uf origin main",
            "git status\ngit push origin --force-with-lease", "bash -c 'git reset --hard'", "sudo make install"]
        for command in cases:
            with self.subTest(command=command):
                result, code = self.event("PreToolUse", "Bash", {"command": command})
                self.assertEqual(code, 2)
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_quoted_messages_are_not_executed_or_false_blocked(self):
        for command in ["echo 'git push --force'", "git status", "git commit -m 'docs: explain git push --force'", "printf '%s' 'rm -rf build'"]:
            with self.subTest(command=command):
                self.assertFalse(bridge.destructive_command(command))

    def test_malformed_command_is_denied(self):
        result, code = self.event("PreToolUse", "Bash", {"command": {"bad": True}})
        self.assertEqual(code, 2)

    def test_cmd_alias_and_argument_array_normalize(self):
        self.assertEqual(bridge.command_text({"cmd": "git status"}), "git status")
        self.assertEqual(bridge.command_text({"command": ["echo", "a b"]}), "echo 'a b'")

    def test_bad_staged_json_denies_commit(self):
        file = self.root / "assets/data/broken.json"
        file.parent.mkdir(parents=True)
        file.write_text('{"broken":')
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        for command in ["git commit -m 'test: broken asset'", "git -C . commit -m 'test'",
                "git status && git commit -m 'test'", "GIT_DIR=.git git commit -m 'test'",
                "bash -c 'git commit -m test'", "git status\ngit commit -m 'test'"]:
            with self.subTest(command=command):
                result, code = self.event("PreToolUse", "Bash", {"command": command})
                self.assertEqual(code, 2, result)
        # An unstaged repair must not conceal invalid JSON still in the index.
        file.write_text('{"fixed":true}')
        result, code = self.event("PreToolUse", "Bash", {"command": "git commit -m 'test'"})
        self.assertEqual(code, 2, result)

    def test_apply_patch_invalid_json_reports_native_feedback(self):
        path = self.root / "Assets/Data/broken.json"
        path.parent.mkdir(parents=True)
        path.write_text("{oops}")
        result, code = self.event("PostToolUse", "apply_patch", {"command": "*** Begin Patch\n*** Add File: Assets/Data/broken.json\n+{oops}\n*** End Patch"})
        self.assertEqual(result["decision"], "block")
        self.assertIn("Invalid asset JSON", result["reason"])
        self.assertTrue(path.exists(), "A post-write hook cannot undo the tool")

    def test_valid_asset_is_not_blocked(self):
        path = self.root / "Content/Data/Valid.json"
        path.parent.mkdir(parents=True)
        path.write_text('{"speed":2}')
        result, _ = self.event("PostToolUse", "Write", {"file_path": str(path)})
        self.assertEqual(result, {})

    def test_shell_writes_are_checked(self):
        path = self.root / "assets/data/new.json"
        path.parent.mkdir(parents=True)
        path.write_text("invalid")
        result, _ = self.event("PostToolUse", "Bash", {"command": "python3 write_asset.py"})
        self.assertEqual(result["decision"], "block")

    def test_nested_cwd_patch_is_checked(self):
        nested = self.root / "Assets"
        nested.mkdir()
        path = nested / "Data/broken.json"
        path.parent.mkdir()
        path.write_text("bad")
        result, _ = self.event("PostToolUse", "apply_patch", {"command": "*** Update File: Data/broken.json\n"}, nested)
        self.assertEqual(result["decision"], "block")

    def test_patch_outside_root_is_denied(self):
        for target in ["../outside.txt", "/tmp/outside.txt", ".env", "src/.env.local"]:
            with self.subTest(target=target):
                _, code = self.event("PreToolUse", "apply_patch", {"command": "*** Add File: " + target})
                self.assertEqual(code, 2)

    def test_symlink_escape_is_denied(self):
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        _, code = self.event("PreToolUse", "apply_patch", {"command": "*** Add File: escape/out.txt"})
        self.assertEqual(code, 2)

    def test_stop_and_compaction_preserve_checkpoint(self):
        path = self.root / "production/session-state/active.md"
        path.parent.mkdir(parents=True)
        path.write_text("Pending: user has not selected an engine\n")
        for event in ["Stop", "PreCompact", "PostCompact", "Interrupt"]:
            result, _ = self.event(event)
            self.assertIn("checkpoint", result["hookSpecificOutput"]["additionalContext"])
            self.assertEqual(path.read_text(), "Pending: user has not selected an engine\n")

    def test_sessionstart_resolves_config_from_root(self):
        nested = self.root / "src"
        nested.mkdir()
        result, _ = self.event("SessionStart", cwd=nested)
        self.assertIn("Review mode: solo", result["hookSpecificOutput"]["additionalContext"])
        self.assertFalse((nested / "production").exists())

    def test_unknown_events_and_malformed_inputs_are_visible(self):
        result, _ = self.event("Notification")
        self.assertIn("Unsupported", result["systemMessage"])
        result, code = bridge.handle({"hook_event_name": "PreToolUse", "tool_input": "bad"}, self.root)
        self.assertEqual(code, 2)

    def test_outside_cwd_is_denied(self):
        _, code = self.event("PreToolUse", "Bash", {"command": "git status"}, self.root.parent)
        self.assertEqual(code, 2)

    def test_lifecycle_log_escapes_metadata_and_excludes_content(self):
        bridge.handle({"hook_event_name": "SubagentStart", "session_id": "a\nforged", "agent_type": "qa-tester", "tool_input": {}, "command": "secret"}, self.root)
        data = (self.root / "production/session-logs/codex-lifecycle.jsonl").read_text()
        self.assertEqual(len(data.splitlines()), 1)
        self.assertEqual(json.loads(data)["session_id"], "a\nforged")
        self.assertNotIn("secret", data)

    def test_lifecycle_can_be_disabled(self):
        (self.root / "project.yaml").write_text("features:\n  session_state: off\n")
        self.event("SubagentStart")
        self.assertFalse((self.root / "production/session-logs").exists())


class ConfigTests(unittest.TestCase):
    def test_yaml_helper_local_rigor_invalid_and_subfolder(self):
        with tempfile.TemporaryDirectory(prefix="config project ") as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / ".codex/hooks", root / ".codex/hooks")
            (root / "project.yaml").write_text("modes:\n  rigor: full\nengine:\n  name: Unity\n")
            (root / "project.local.yaml").write_text("modes:\n  review_mode: solo\n")
            sub = root / "Assets"
            sub.mkdir()
            cmd = ["bash", str(root / ".codex/hooks/yaml-helper.sh"), "resolve_config", "--keys", "review_mode,workflow,qa.level"]
            result = subprocess.run(cmd, cwd=sub, text=True, capture_output=True, check=True)
            self.assertIn("review_mode: solo (project.local.yaml)", result.stdout)
            self.assertIn("workflow: full (rigor:full)", result.stdout)
            (root / "project.local.yaml").write_text("modes:\n  review_mode: chaotic\n")
            result = subprocess.run(cmd, cwd=sub, text=True, capture_output=True, check=True)
            self.assertIn("review_mode: full", result.stdout)
            self.assertIn("chaotic", result.stdout)


class RuleTests(unittest.TestCase):
    def test_three_engines_and_zero_depth_globstar(self):
        for path in ["src/gameplay/health.gd", "Assets/Gameplay/Health.cs", "Assets/Game/Gameplay/Logic/Health.cs", "Source/Game/Gameplay/Health.cpp", "Source/Game/gameplay/Health.h"]:
            with self.subTest(path=path):
                self.assertIn(".codex/rules/gameplay-code.md", rules.route(path)["rules"])

    def test_unrelated_paths_do_not_load_gameplay_rule(self):
        self.assertNotIn(".codex/rules/gameplay-code.md", rules.route("docs/gameplay-notes.md")["rules"])

    def test_brace_expansion_is_complete(self):
        self.assertEqual(len(rules.expand_braces("{a,b}/{c,d}")), 4)

    def test_outside_rule_path_rejected(self):
        with self.assertRaises(ValueError):
            rules.route("../other-project/file.gd")


class MigrationTests(unittest.TestCase):
    def test_generated_layer_is_complete_and_reproducible(self):
        result = validate_codex.validate()
        self.assertEqual(result["status"], "PASS", "\n".join(result["errors"]))
        self.assertEqual((result["skills"], result["roles"]), (74, 49))

    def test_prompt_arguments_are_not_shell_code(self):
        text = port_to_codex.adapt('`$ARGUMENTS`\n!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config`', ["start"])
        self.assertNotIn("$ARGUMENTS", text)
        self.assertNotIn("!`", text)
        self.assertIn("Run explicitly", text)

    def test_skill_names_are_namespaced_and_refs_relocated(self):
        result = port_to_codex.adapt("/help .claude/skills/help/SKILL.md .claude/agents/producer.md", ["help"])
        self.assertEqual(result, "$gs-help .agents/skills/gs-help/SKILL.md .codex/agents/producer.toml")

    def test_unsupported_metadata_cannot_sneak_into_native_skill(self):
        meta, _ = port_to_codex.frontmatter((ROOT / ".agents/skills/gs-dev-story/SKILL.md").read_text())
        self.assertEqual(set(meta), {"name", "description"})


if __name__ == "__main__":
    unittest.main()
