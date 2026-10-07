# 本地项目工作区

在此保存本机创作项目。真实项目目录、项目索引 `index.yaml` 默认被 Git 忽略，防止个人资料、素材、未发布草稿和审批状态随系统代码分发。公开仓库只保留空白索引模板 `index-temp.yaml`，不包含你的真实项目列表。

首次使用时，复制 `index-temp.yaml` 为 `index.yaml`（也就是把副本文件名中的 `-temp` 后缀去掉）：

```powershell
Copy-Item projects/index-temp.yaml projects/index.yaml
```

`index.yaml` 是本机生成的索引，不要提交或上传。运行 Workflow 的 `init` 或 `rebuild-index` 后，系统会根据本机项目重新生成该文件；一般无需手工编辑。

创建项目：

```powershell
uv run python modules/workflow/scripts/studio.py init --project <project-id> --name "<项目名>" --kind knowledge
```

确需分享项目时，先审查素材权限、隐私、内容状态和审批记录，再通过独立的项目交付包显式导出。
