# Codex 迁移任务、依赖与验收

上游基线：Donchitos/Claude-Code-Game-Studios，v1.1.3，
`be8993bbc5a1f016bc770b2846ce06272d284526`。
目标：保留原始来源和许可，增加 Codex 原生入口、技能、角色与检查适配。
“配置能解析”“实际自动加载”“模型遵循流程”“游戏运行正确”分别验收。

## 改写前的任务拆分

下表的并行是依赖允许的组织方式。本次没有启动额外代理；实际实现由当前会话完成。

| ID | 具体任务 | 依赖与串并行 | 完成条件与验证 | 对抗验证与失败处理 |
| --- | --- | --- | --- | --- |
| T1 | 确认 GitHub 身份、fork、固定上游提交、保存许可和原始层 | 起点，必须串行 | fork 归属当前用户；GitHub 显示上游关系；远端提交与基线一致；MIT 和原始文件保留 | 检查误写上游、已有 fork、错误默认分支；操作前核对 owner、origin、upstream |
| T2 | 清点技能、角色、规则、hooks、脚本；核对 Codex 原生接口 | T1 后串行；是后续共同契约 | 清单覆盖 74 技能、49 角色；逐项记录路径与原始元数据；核对官方文档及本机 schema | 搜索遗留专用字段、隐式 shell 注入、工具名和路径；无法确认接口时不能编造能力 |
| T3 | 构建 AGENTS.md、规则读取器和配置解析适配 | T2 后，可与 T4/T5 并行 | 根目录和子目录都解析同一项目；路径规则正确选择；配置优先级、无效枚举回退正确 | 空格路径、嵌套 cwd、符号链接、`**/` 零层匹配、花括号展开、非法配置；新增回归后修复 |
| T4 | 迁移 74 技能及其阶段引用到 `.agents/skills/gs-*` | T2 后，可与 T3/T5 并行；最终依赖 T3/T6 | 原生 name/description；名称不冲突；引用存在；参数来自用户请求；重生成无漂移 | 禁止 Claude 内联预处理和不存在的工具调用；缺引用、改元数据、命令注入样例必须失败 |
| T5 | 迁移 49 角色到 `.codex/agents/*.toml` | T2 后，可与 T3/T4 并行；最终依赖 T6 | 每个 TOML 有 name、description、developer_instructions；默认继承模型；只读角色保留只读权限 | 检查模型硬编码、权限扩大、同名角色、Claude tools/maxTurns 等不支持字段；原生启动另外验收 |
| T6 | 迁移工具和生命周期 hooks，处理真实事件 JSON | T2 后，可与 T3/T4/T5 并行；集成时串行 | native hook 输出；提交前校验；写入后反馈；Stop/压缩保留检查点；失败可见 | 坏 JSON、未知事件、命令别名、链式危险命令、路径逃逸、伪造日志、禁用配置；不实际执行破坏命令 |
| T7 | 确定性生成、结构与行为回归、原生与游戏验证 | T3–T6 集成后串行；不同测试层可并行 | 生成一致、全部引用/元数据有效、单元测试通过；原生加载和真实玩法单独给证据 | 刻意构造反例并检查拒绝/未验证状态；失败→复现→回归用例→修复→重测；禁止把缺证据当通过 |
| T8 | 中英文说明、使用入口、限制和实际验收记录 | 说明草稿可与 T3–T6 并行；结果必须等 T7 | 从新 checkout 按 README 执行检查；验证报告与真实输出一致；注明项目/hook 信任条件 | 检查过时路径、原生命令冲突、虚构成功与“未验证”的漏报；修正文案并检查链接 |
| T9 | 推送用户 fork 的独立分支、PR 和跨平台 CI | T7/T8 后串行 | 远端 SHA 和内容一致；PR 只指向用户 fork；CI Ubuntu/macOS 结果可追溯 | 核对错误仓库、漏文件、生成漂移、跨平台行为差异；CI 失败取日志复现修复，再次推送 |

## 接口选择

- 技能以 `$gs-*` 调用，避免与 Codex 的 `/help`、`/settings` 冲突。
- 文档以显式读取方式加载；不能假定 `@` 文档导入或 Markdown 路径规则会自动运行。
- 原 Claude 的角色工具与流程操作映射见 `.codex/docs/codex-runtime.md`。
  使用当前宿主实际暴露的工具。没有代理能力时顺序执行，不宣称已经委派。
- 配置和 hook 信任使用 Codex 正常审阅流程。配置文件不授予额外用户授权。
- 原始 `.claude/` 和测试框架保留；改写层用来源哈希和确定性生成记录追踪。

官方接口参考：
[Skills](https://learn.chatgpt.com/docs/build-skills)、
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、
[Hooks](https://learn.chatgpt.com/docs/hooks)、
[Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)。

## 验证层级和停止标准

1. 离线层：结构、生成一致性、路径和真实脚本逻辑必须全部通过。
2. 原生层：在受支持的 Codex 客户端上实际发现技能、加载配置、启动一个只读角色，
   并验证已审阅的 hook 确实被调用。只解析 TOML 不能代替这一层。
3. 模型行为层：运行 `$gs-settings` 读取覆盖配置、`$gs-dev-story` 的小任务、
   `$gs-story-done` 缺证据反例；后者必须拒绝把没有实际测试/截图的项目记为通过。
4. 游戏层：选定 Godot/Unity/Unreal 后完成构建、测试、运行和真实画面验收。

受环境阻挡的层级标为 NOT ASSESSED，保留可复现命令和阻挡原因。
不得为了通过而删掉反例、放宽断言或声称完成未运行的验证。
