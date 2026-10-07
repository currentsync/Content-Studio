# 第三方来源与许可清单

本项目采用逐来源、逐范围管理许可的方式。此清单与各材料随附的原始许可共同适用。

| 来源 | 仓库位置 | 许可与说明 |
| --- | --- | --- |
| huashu-art-motion 代码与文档 | 逐文件范围见 `third-party/huashu/FILE-SCOPE.csv` | MIT；版权与许可文本见 `third-party/huashu/MIT.txt`。清单中的文件可能经过本项目修改；Huashu 的 MIT 许可仅覆盖其来源清单中的文件，不覆盖 ContentStudio 原创部分。 |
| 花叔卡通形象和角色帧 | 上游 `scripts/engine/demos/_shared/hero/`、`scripts/engine/demos/long_scroll/frames/`；ContentStudio 不包含这些素材 | 上游说明这些素材只用于 Huashu Skill 的示范，不随 MIT 授权用于其他用途。没有单独许可，因此不纳入 ContentStudio 公开分发。改编示例请使用自有或明确允许再分发的素材。 |
| 汉字笔画中线数据 | `modules/creative/reference-projects/spacex/spacex_wb/assets/strokes.js` | Arphic Public License；原文随附于同目录 `ARPHICPL.TXT`。不属于 Huashu MIT 范围。 |
| Canvas 字体 | `modules/production/engines/canvas/fonts/` | SIL Open Font License 1.1；字体名、版权和来源见 `fonts/LICENSES.md`，全文见 `fonts/OFL.txt`。 |
| Python 与浏览器运行依赖 | `pyproject.toml`、`uv.lock` | 各依赖保留其自身许可证；分发二进制或依赖副本时应另外生成并审阅依赖许可证清单。 |
| 示例媒体、参考图和项目资产 | `modules/creative/examples/`、`modules/creative/reference-projects/` | 按各自 manifest 和来源记录限定用途；不得仅因进入本仓库就推断为可商用或可再分发。 |

上游整合映射和历史迁移记录存放于本项目工作区外的项目档案中，不作为运行时依赖，也不随此产品仓库分发。

