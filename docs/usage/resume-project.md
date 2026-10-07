# 创建与恢复项目

项目的唯一进度快照是 `projects/<project_id>/project.yaml`。Agent 新开会话时先运行 `status` 与 `next`，按快照和对应 Skill 继续，不从聊天记录或运行日志猜测进度。

## 创建一个知识项目

```powershell
uv run python modules/workflow/scripts/studio.py init --project <project-id> --name "项目标题" --kind knowledge
```

`init` 创建 `project.yaml` 和 Editorial 持有的 `brief.yaml`，并更新索引。知识项目从 Idea 开始，Core 状态为 `missing`；账号介绍和历史媒体项目使用 `account_intro`、`legacy_media` 类型，不套用知识项目阶段。

## 查看当前工作

```powershell
uv run python modules/workflow/scripts/studio.py status --project <project-id>
uv run python modules/workflow/scripts/studio.py next --project <project-id>
```

`next` 返回待办、负责模块、Skill 路径和已有产物引用。`waiting_for_user` 有内容时先请求指定确认，不继续越过人工选择。

## 登记模块结果

执行模块写入自己负责的项目产物后，向 Workflow 返回实际路径与输入。Workflow 使用 `record` 写入快照和运行记录：

```powershell
uv run python modules/workflow/scripts/studio.py record --project <project-id> --operation <operation> --result succeeded --input <项目相对输入> --output <项目相对产物>
```

产物和输入必须存在于该项目目录内。失败或阻塞要带 `--detail`。只有用户真实确认后才使用 `confirm`，确认记录绑定到产物 SHA-256。

运行历史用于定位某次执行的结果；项目当前进度只读项目快照。
