# Codex 游戏开发工作室

这是 [Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
的 Codex 适配分支，保留上游许可和历史。包含 74 个技能、49 个角色以及策划、
开发、测试和发布流程。它是开发模板，使用时仍需要游戏引擎。

## 开始使用

需要 Python 3.11+、Git、Bash 和支持项目技能与自定义角色的 Codex。

```bash
git clone --branch codex-port https://github.com/allenye/Codex-Game-Studios.git my-game
cd my-game
python3 tools/validate_codex.py
codex
```

输入 `$gs-start`，或者直接描述游戏目标。常用命令：

- `$gs-setup-engine`：配置 Godot、Unity 或 Unreal。
- `$gs-brainstorm`：整理玩法和小原型范围。
- `$gs-create-stories` → `$gs-dev-story` → `$gs-story-done`：拆任务、实现、验收。
- `$gs-settings modes.rigor`：查看流程严格程度。
- `$gs-code-review`、`$gs-smoke-check`：审查和验证。
- `$gs-help`：查看下一步。

先按 Codex 的正常流程信任项目配置；检查 `.codex/hooks.json` 和关联脚本，
再通过 `/hooks` 审阅并信任检查钩子。尚未信任时不能假设钩子已经执行。
适配不会修改你的全局设置，也不会锁定模型。角色默认继承会话模型。

## 验证与限制

```bash
python3 tools/port_to_codex.py --check
python3 tools/validate_codex.py
python3 -m unittest discover -s tests/codex_port -v
```

测试包括坏 JSON、嵌套目录、空格路径、符号链接、配置覆盖和会话恢复。
失败后按“复现 → 回归用例 → 修复 → 重测”处理。

结构检查、原生 Codex 加载、实际模型行为和游戏运行是不同验收层级。
没有引擎、实际运行记录或真实截图时应报告“未验证”，不能宣布通过。
详见 [任务与依赖](docs/CODEX-MIGRATION-PLAN.md) 和
[实际验证报告](docs/CODEX-VALIDATION.md)。

原始 `.claude/` 保留用于追溯；Codex 使用 `AGENTS.md`、`.agents/skills/`
和 `.codex/`。更改生成文件时请修改 `tools/codex-overrides/` 后重新生成。
