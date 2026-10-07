---
name: creative-media-execution
description: 在 Editorial 已确认内容且 CreativePlan 已确认后，实现代码绘制动画、视觉片段或风格场景。只负责画面实现与制作适配，不决定内容主张和是否采用某种风格。
---

# Creative 媒体实现

## 执行前提

先读取项目中的已确认制作稿、CreativePlan、素材清单和 ProductionRequest。风格推荐及镜头目的由 `direct-visual-story` 负责；本 Skill 根据批准的方向实现画面。如果事实依据、镜头目的、素材授权或交付参数缺失，返回具体问题给 Workflow，不自行补造。

## 视觉实现方法

- 用 Canvas 程序化绘制图表、形状、标注、路径和运动；真人或复杂角色使用有来源的图像/sprite，代码负责合成、位置、缩放、换帧和运镜。
- 复刻参考时提取画面机制、节奏和转场规则，再为当前内容编排。参考工程不是可直接替换文案的成片模板。
- 动画要服务当前镜头的理解目标。镜头中的事实、数量、人物和因果必须能追溯到 Editorial 引用；视觉风格不能改变内容含义。
- 使用确定性随机种子；检查关键时间点、字幕安全区、素材边界和过渡帧。任何不能从证据或 CreativePlan 推导的画面信息都要提请澄清。

## 本地能力地图

| 用途 | 路径 |
| --- | --- |
| Canvas 运行时、HTML 入口、字体与资源映射 | `modules/production/engines/canvas/` |
| 可复用场景、动画语法片段与转场 | `modules/creative/canvas/` |
| 风格卡、语法卡及实现配方 | `modules/creative/styles/` |
| 可运行演示与参考工程 | `modules/creative/examples/`、`modules/creative/reference-projects/` |
| CreativePlan 校验 | `modules/creative/scripts/validate_plan.py` |
| 媒体渲染 | `modules/production/scripts/render_canvas.py` |
| 技术 QA 与成片审阅 | `modules/review/scripts/` |

优先读取 `modules/creative/styles/index.yaml`，确认风格能力、素材前提和示例用途。`demo_only` 素材不能进入正式作品。Vox、Kurzgesagt、白板、玻璃 UI、手绘等表现方式各自遵从对应语法卡，不把某种视觉组件强加给不适用的风格。

## 执行方式

正式项目使用项目内 ProductionRequest：

```powershell
uv run python modules/production/scripts/render_canvas.py --request projects/<project-id>/channels/<target-id>/production/request.yaml --preview --out projects/<project-id>/channels/<target-id>/production/preview/
```

临时学习本地参数化片段时，可以用仓库示例；输出只写到临时目录或当前项目：

```powershell
uv run python modules/production/scripts/render_canvas.py --spec modules/creative/examples/clips/y2_vox.json --preview --out .tmp/vox-preview/
```

代表帧通过后，再按 ProductionRequest 渲染或组装完整媒体。把请求、使用的素材引用、预览和实际产物路径交回 Workflow 登记；不直接改 `project.yaml`。

## 检查与交接

1. 对照制作稿逐镜核查画面，不引入新事实；必要时由 Review 回查主张依据。
2. 检查画幅、帧率、时长、字体、图像授权、字幕安全区和关键转场。
3. 将技术问题交回 Creative/Production 的对应负责人；Review 独立检查成片，不由制作 Agent 自行通过。
4. 新版本使用新产物路径并计算指纹。文件变化后，旧 ReviewReport 和用户确认不再适用于新版本。

上游方法的来源和许可见 `third-party/huashu/README.md`；这里的目录描述以当前 Content Studio 实现为准。
