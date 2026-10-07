# Content Studio agent rules

本仓库的工作名为 Content Studio（内容工坊）。Agent 通过项目文件和模块 Skills 协作，不运行常驻服务或后台队列。

## 决策职责

- Editorial 决定内容主张、证据、边界和渠道表达；不决定具体视觉样式。
- Creative 根据内容目标和可用素材选择风格、镜头与视觉叙事，并提出重要方向供用户确认。
- Production 执行已确认方案中的工程、资源、声音、字幕、渲染和组装；不改内容主张或风格。
- Workflow 是唯一项目状态写入者；执行模块只写自己负责的产物。
- Review 独立检查内容和媒体；问题写明位置、责任模块与复核条件。

## 工作约定

- 使用 UTF-8；跨模块引用使用仓库或项目内相对路径，并校验路径不越界。
- `projects/<id>/project.yaml` 是唯一项目进度快照；`projects/index.yaml` 是可重建索引，`runtime/runs.jsonl` 是诊断记录。
- 只有真实用户行为才登记为确认；运行成功、迁移指纹和示例内容都不构成用户批准。
- 未确认的内容、素材来源或交付要求要明确列为缺项，不推断为已通过。
- 迁移现场文件先核对来源、去向和改动；只有隔离验证与备份核对通过后才清理旧目录。
- 优先复用现有 Skills 和实现。新增常驻服务、数据库或任务平台前必须先证明现有文件与脚本无法满足需求。

## Formal entry points and delivery gate

- Start projects with `uv run python modules/workflow/scripts/studio.py`. Read `projects/<id>/project.yaml` and `brief.yaml`, then follow the module/Skill and todo returned by `next`.
- Before delivery confirmation, an independent reviewer must complete a ReviewReport bound to the current artifact SHA-256 and validate it with `modules/review/scripts/report.py --report ...`. Technical QA is not content review or user approval.
- `delivery` and `complete` must reference the same path and digest. A changed media version needs a new review and confirmation; archive checks the report, digest, approvals, and open work again.
- huashu capabilities are accessed through repository-owned adapters in `modules/creative/` and `modules/production/`. Formal projects must reference only assets and tools inside this repository or their own project directory.
