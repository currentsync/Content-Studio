# 从示例改编为正式项目

示例用于看实现机制和起步预览。正式内容必须由本项目 Editorial 提供，镜头表达由 Creative 根据理解目标选择；不要把示例中的数字、角色、论文截图或叙事当作本项目事实。

## 操作步骤

1. 创建知识项目，并按 `docs/usage/resume-project.md` 完成 Idea、Core、渠道内容和用户确认。
2. 在 `modules/creative/examples/README.md` 选一个最适合解释任务的示例。Vox 适合真实档案材料驱动的调查表达；机制推演通常优先考虑 `t1_3b1b` 或白板；有实际对比数据时再考虑 `t3_finance_chart`。
3. 将可复用的语法配置复制到项目，例如将 `modules/creative/examples/clips/y2_vox.json` 复制为 `projects/<id>/channels/bilibili-video/creative/native/clip.json`。只复制结构作起点，不沿用其示例事实和媒体文件。
4. 把本项目脚本与来源明确的素材放在同一项目中。创建 `assets/manifest.yaml` 并为每项素材记录来源、许可和 `allowed_usage: production`；示例人物或演示素材要标为 `demo_only`，Creative 校验会拒绝把它们当作正式素材。
5. 填写 `creative/plan.yaml`，每个单元引用对应稿件段落并说明理解目标。执行 `uv run python modules/creative/scripts/validate_plan.py --project <id> --plan channels/bilibili-video/creative/plan.yaml`。
6. 根据确认后的方案创建 `channels/bilibili-video/production/request.yaml`。`native_input` 指向项目内 clip spec 并带有实际 SHA-256；`output.path` 指向项目内待生成候选文件。
7. 先用代表帧给用户确认方向，再完整渲染；媒体渲染和审阅流程见 `docs/usage/create-and-deliver.md`。方向确认、结果登记都由 Workflow 执行。

当前 `y6_presenter_explainer` 只有指南和部分参考工程，没有成套人物帧与音频。八个可运行 clip 和长卷也不等于自动配音云服务；声音输入在项目端提供后才进入同步与字幕制作。
