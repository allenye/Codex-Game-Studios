# Codex 适配实际验证报告

记录时间：2026-10-10（Asia/Shanghai）。上游固定为 v1.1.3，提交
`be8993bbc5a1f016bc770b2846ce06272d284526`。

## 已完成的改写

- fork 属于 `allenye/Codex-Game-Studios`；改写在 `codex-port` 分支。
- 74 个技能迁移到 `.agents/skills/gs-*`，阶段资源保留、引用重新定位。
- 49 个角色迁移到 `.codex/agents/*.toml`；不指定模型；原只读角色保持只读。
- 新增 AGENTS.md、显式路径规则读取器、原生执行策略和 10 种 hook 事件适配。
- 原始 `.claude/`、测试框架、Git 历史和 MIT 许可保留。
- 确定性生成器、来源哈希清单、中英文使用说明及 Ubuntu/macOS CI 已加入。

## 验证结果

| 层级 | 实际执行 | 结果 | 证明范围 |
| --- | --- | --- | --- |
| 生成一致性 | `python3 tools/port_to_codex.py --check` | PASS | 所有受生成器管理的文件与来源/语义覆盖一致 |
| 结构与引用 | `python3 tools/validate_codex.py` | PASS：74 skills、49 roles、0 defects | 名称、原生元数据、TOML、JSON、路径、shell 语法、来源哈希；不证明模型执行 |
| 独立技能检查 | skill-creator 的 `quick_validate.py` + PyYAML 6.0.3，逐个验证 74 个技能 | PASS：0 defects | 真实 YAML 解析器验证技能 frontmatter、描述和命名约束；PyYAML 仅用于本次 QA，用户检查不依赖它 |
| 回归与反例 | `python3 -m unittest discover -s tests/codex_port -v` | PASS：26 tests，包含多项 subTest | 直接调用实际 bridge、配置 helper、规则读取器；临时 Git 仓库中验证提交拒绝；没有实际执行危险命令 |
| 原生执行策略 | `codex execpolicy check --rules .codex/rules/studio.rules -- git push --force origin main` | PASS：decision=forbidden | 本机 Codex 能解析该策略并匹配这一危险前缀；未执行 push |
| 原生技能加载 | app-server `initialize` → `skills/list`；`python3 tools/check_native_codex.py` | NOT ASSESSED | 当前宿主沙箱中 app-server 在 initialize 前退出：`Operation not permitted (os error 1)` |
| 实际角色和 hook 调用 | 需要正常客户端、项目信任和精确 hook 信任 | NOT ASSESSED | TOML 和 hook handler 测试不能代替角色启动/宿主 hook 调用 |
| 模型行为 | 需要实际 `$gs-settings`、开发与缺证据反例运行 | NOT ASSESSED | 没有声称 74 个完整工作流都经过真实模型验收 |
| 游戏构建/运行/画面 | 需要选定并安装游戏引擎与项目 | NOT ASSESSED | 未安装/运行引擎，没有生成或冒充游戏截图 |
| 远端 CI | PR 中的 Codex port checks，Ubuntu/macOS | 以 GitHub Checks 实际记录为准 | 文档不把“已添加 CI”写成“远端 CI 已通过” |

本机检查使用 Python 3.14 和 codex-cli 0.162.0-alpha.2；CI 指定 Python 3.11。
因此旧版 Codex、Windows Bash/引擎安装和桌面端的所有能力均未认证。

## 对抗验证与已修复缺陷

1. **macOS 路径别名**：临时目录 `/var/...` 和 `/private/var/...` 指向相同位置。
   首次反例导致合法的根目录被误判为越界。将 bridge 根目录规范化为真实路径，
   保留带空格的临时目录测试并重跑整套验证。
2. **坏引用**：结构检查发现不存在的 patch-notes-template 和错误的
   `.codex/AGENTS.md` 引用。新增真实发布说明模板，并将入口引用改为根 AGENTS.md；
   重新生成后检查为 0 defects。没有删除引用断言来掩盖错误。
3. **提交与写入反例**：坏 asset JSON、链式命令、Git 全局选项、包装 shell、
   多行命令和“索引仍坏、工作副本已修好”均须拒绝提交。
   写入后的坏 JSON 返回原生 block 反馈；测试同时确认文件仍存在，防止虚构回滚。
4. **路径反例**：嵌套 cwd、空格目录、越界路径、符号链接逃逸和环境文件写入。
   检查实际路径而非只匹配字面前缀；拒绝不允许的写入。
5. **生命周期反例**：Stop/压缩/中断后检查点保留；未知事件和坏输入可见；
   日志元数据中的换行不能伪造额外 JSONL 行；日志不记录命令或会话正文；禁用开关生效。
6. **规则与配置反例**：Godot、Unity、Unreal 三种路径；globstar 零层；完整花括号
   展开；无关文件；本地覆盖；rigor 默认；无效枚举回退；子目录读取同一配置。
7. **权限边界**：普通提示性操作与危险命令区分；已引用的危险文字不能被当成执行。
   Shell 文本扫描只覆盖常见形式，不是完整 shell 解释器或安全边界。

优化循环固定为：观察失败 → 保存复现 → 增加/保留反例 → 修复原因 → 重跑相关检查 →
运行整套相关回归。没有证据的验收维持 NOT ASSESSED。

## 在正常 Codex 环境中补完验收

```bash
git clone --branch codex-port https://github.com/allenye/Codex-Game-Studios.git my-game
cd my-game
python3 tools/port_to_codex.py --check
python3 tools/validate_codex.py
python3 -m unittest discover -s tests/codex_port -v
python3 tools/check_native_codex.py
codex
```

技能发现脚本不启动模型会话、不修改信任设置；exit 2 表示未验证。
在客户端正常流程中审阅项目配置，阅读 `.codex/hooks.json` 与对应脚本，
通过 `/hooks` 审阅并信任精确内容后再检查 hook 是否实际调用。

随后逐项记录真实输出：

| 场景 | 预期 | 失败后的对抗复测 |
| --- | --- | --- |
| 根目录和 `src/` 中发现 `$gs-start`、`$gs-settings` | 发现同一套 74 个技能 | 新 checkout、带空格路径、子目录；记录实际客户端版本与加载错误 |
| `$gs-settings modes.rigor` | 从 helper 读取当前值与来源 | 在临时项目增加 local 覆盖和无效值；确认结果及回退来源，无写入污染 |
| 明确要求启动一个 qa-tester 只读子代理 | 真正的子代理工具调用与只读行为 | 尝试越界写入；没有真实调用不能记“委派成功” |
| `$gs-story-done` 但缺少运行结果/必要截图 | 保持未验收；列出缺失证据 | 提供看似完整但没有运行来源的文字或图片；不得伪造 PASS |
| Stop 后继续未完成任务 | 读取原检查点并继续 | 保留未回答的用户决策；不得从默认值或沉默推断授权 |
| 用 `$gs-setup-engine` 创建最小游戏，再开发一条 story | 配置、构建、测试、启动、画面一致 | 故意提供失败测试、错误引擎版本、错误项目路径；应报告失败并修复重测 |

所有实际运行日志、真实画面和结论应保存在项目的 production 记录中。
