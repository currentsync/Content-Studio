# Content Studio（内容工坊）

Content Studio 是面向 Agent 的内容创作与媒体制作工作流：从选题、知识核查、渠道表达、视觉创作、媒体制作、独立审阅，到用户交付和归档。文件是工作载体，`project.yaml` 是项目状态真源；系统不依赖常驻服务、任务队列或独立数据库。

## 开始使用

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 Chromium（Canvas 渲染时使用）。

```powershell
uv sync
uv run python modules/workflow/scripts/studio.py init --project <project-id> --name "<项目名>" --kind knowledge
uv run python modules/workflow/scripts/studio.py next --project <project-id> --target bilibili
```

恢复项目时先读 `projects/<project-id>/project.yaml` 和 `brief.yaml`，再遵循 `next` 返回的负责人、Skill 和前置条件。完整操作见[从选题到交付](docs/usage/create-and-deliver.md)、[恢复项目](docs/usage/resume-project.md)和[示例改编](docs/usage/adapt-example.md)。

## 模块

| 模块 | 职责 |
| --- | --- |
| Editorial | Core、证据与范围、渠道表达、制作稿 |
| Creative | 根据内容目标选择风格、编导镜头与视觉实现 |
| Production | 素材、Timing、字幕、渲染、装配与媒体属性 |
| Review | 独立审阅内容、视听质量和交付完整性 |
| Workflow | 路由、项目快照、恢复、确认与归档门禁 |

Editorial 拥有内容主张、证据和限制；huashu 视觉方法只作为 Creative/Production 的实现能力，不能反向决定内容。示例素材按清单限定用途。

## 目录

```text
contracts/   跨模块 JSON Schema 与最小示例
modules/     五个 Agent 模块、Skills 与媒体实现
projects/    本地项目工作区（真实项目与 index.yaml 不纳入 Git；仅发布空白模板）
runtime/     本地运行日志和临时状态
third-party/ 上游许可和第三方声明
docs/usage/  面向使用者的操作说明
docs/architecture/ 系统架构与模块设计规格
```

公开的[总体架构设计](docs/architecture/architecture.md)和[模块设计与交接](docs/architecture/module-design.md)随产品仓库提供。整合迁移记录和产品营销材料仍单独保存在项目工作区之外，不随产品仓库分发。

## 质量与交付

交付确认要求当前产物有独立 ReviewReport，报告绑定现存文件指纹、结论通过且没有未解决阻断项。`delivery` 和 `complete` 必须确认同一版本；文件变化或重新交付会要求重新审阅和确认。技术测量不代替内容事实与理解效果判断。

```powershell
uv run python modules/workflow/scripts/studio.py check
uv run python modules/review/scripts/report.py --project <project-id> --target <target-id> --report channels/<target-id>/review/<review-id>.yaml
```

## 项目数据与分发

`projects/` 中的真实项目和 `index.yaml`、以及 `runtime/` 中的运行数据默认被 Git 忽略。仓库只提供空白索引模板 `projects/index-temp.yaml`；首次使用可复制成 `projects/index.yaml`，详见 [`projects/README.md`](projects/README.md)。分享系统代码时不会顺带提交个人项目、内容草稿、项目清单或运行日志；需要分享某个内容项目时，应单独审查并显式导出。

组件许可范围见 [LICENSE](LICENSE) 与 [LICENSE-SCOPE.md](LICENSE-SCOPE.md)，第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

