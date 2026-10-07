# 从选题到交付

本流程由 Workflow 调度五个模块。Editorial 对内容与知识依据负责，Creative 为已确认内容选择适合的视觉风格，Production 执行素材与媒体制作，Review 独立检查具体版本，Workflow 保存唯一项目状态并执行交付门禁。

## 1. 建立项目并恢复工作

```powershell
uv run python modules/workflow/scripts/studio.py init --project <project-id> --name "<项目名>" --kind knowledge
uv run python modules/workflow/scripts/studio.py status --project <project-id>
uv run python modules/workflow/scripts/studio.py next --project <project-id> --target bilibili
```

Agent 先读取 `project.yaml` 和 `brief.yaml`，再按 `next` 给出的 `owner`、Skill 与前置条件工作。选题、受众、学习目标及交付约束写入项目 brief；Workflow 不替 Editorial 或 Creative 做内容判断。

## 2. 形成已确认的内容方案

Editorial 按序完成 Core、Base 内容、Shell、渠道稿、标题/开场和口播制作稿。内容稿保留论点、证据、限定条件、口播文本与镜头所需的内容依据。需要用户选择或确认时，Workflow 在 `waiting_for_user` 中登记具体问题并暂停下游。

每一步完成后，Workflow 登记产物和实际输入引用：

```powershell
uv run python modules/workflow/scripts/studio.py record --project <project-id> --operation <workflow-step> --result succeeded --output <project-relative-path> --input <project-relative-input>
```

`record` 计算 SHA-256 并更新项目快照。源文件变化后，`next` 和 `check` 会提示受影响的引用需要重做或复核。

## 3. Creative 选择视觉实现

Creative 读取已确认的制作稿、素材清单和交付要求，独立推荐适配的风格并说明理由；用户确认方向后，生成 `channels/<target>/creative/plan.yaml`。镜头要引用内容依据和素材，不得让画面补充未经证实的事实。示例素材的 `demo_only` 范围不能用于正式交付。

## 4. Production 制作

Creative/Workflow 将制作输入固化为项目内 `ProductionRequest`，并为具体引擎准备原生输入。Production 按请求执行代表帧/片段渲染、Timing 与字幕准备、镜头片段组装。请求声明了画幅、帧率、时长、口播或字幕要求时，执行器必须据实验证；新候选使用新路径，不能覆盖已有或已批准版本。

完成后检查项目产物引用与媒体实际属性：

```powershell
uv run python modules/workflow/scripts/studio.py check --project <project-id>
uv run python modules/production/scripts/probe_media.py projects/<project-id>/<candidate-path> --expected-duration <seconds>
```

## 5. 独立审阅当前版本

Review 读取实际媒体、内容证据、Creative 方向和技术 QA 输出，按镜头/时间记录问题及责任模块。技术测量与内容/理解效果判断分开记录；QA 通过不能代替事实核验。

为当前实际产物生成带指纹的审阅草稿：

```powershell
uv run python modules/review/scripts/report.py --project <project-id> --target <target-id> --create --review-id <review-id> --artifact channels/<target-id>/production/<candidate-file> --scope "内容准确性" --scope "视觉解释与字幕" --scope "交付完整性"
```

独立 Reviewer 检查文件并编辑 `channels/<target-id>/review/<review-id>.yaml`：补全实际检查范围、发现项和结论；只有亲自审阅该版本的角色才设置 `independent: true`，结论通过且不存在未解决阻断项时才能写 `conclusion: pass`。验证报告及文件指纹：

```powershell
uv run python modules/review/scripts/report.py --project <project-id> --target <target-id> --report channels/<target-id>/review/<review-id>.yaml
```

更改已审阅的任何输入或成片后，需对新版本重新审阅。旧报告不会放行新指纹。

## 6. 用户确认并归档

用户检查通过版本后，记录真实确认及同一产物 SHA-256。PowerShell 可用 `Get-FileHash -Algorithm SHA256 <path>` 获取指纹：

```powershell
uv run python modules/workflow/scripts/studio.py confirm --project <project-id> --kind delivery --artifact channels/<target-id>/production/<candidate-file> --sha256 <sha256> --evidence "<实际交付确认依据>"
uv run python modules/workflow/scripts/studio.py confirm --project <project-id> --kind complete --artifact channels/<target-id>/production/<candidate-file> --sha256 <sha256> --evidence "<实际项目完成确认依据>"
uv run python modules/workflow/scripts/studio.py archive --project <project-id>
```

delivery 与 complete 必须指向同一版本，且当前版本须有最新、独立、通过的 ReviewReport。文件改变、审阅不过、仍有待办或等待项时，Workflow 阻止确认或归档。确认只能记录真实用户行为，不用 Agent 推断或代填。

## 责任交接

| 上游 | 交给下游 | 下游职责 |
| --- | --- | --- |
| Editorial | 已确认内容稿、证据/限制引用、理解目标 | Creative 选择如何表达，不改写事实边界 |
| Creative | 风格方向、镜头目的、内容依据、素材需求、ProductionRequest | Production 依请求实现，不替 Creative 决定叙事 |
| Production | 带 SHA-256 的媒体候选、Timing、ArtifactManifest、技术测量 | Review 检查实际版本及可交付性 |
| Review | 独立 ReviewReport：审阅指纹、范围、问题归属与结论 | Workflow 只接受当前指纹对应的通过报告 |
| Workflow | 项目快照、路由、阻塞和确认/归档门禁 | 单独写 `project.yaml` 与派生索引 |
