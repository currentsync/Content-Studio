"""Repository and project path resolution with traversal protection."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECTS = ROOT / "projects"
ARCHIVE = PROJECTS / "archive"
RUNTIME = ROOT / "runtime"


def project_dir(project_id: str, *, archived: bool = False) -> Path:
    if not project_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for ch in project_id):
        raise ValueError(f"无效 project_id：{project_id!r}")
    base = ARCHIVE if archived else PROJECTS
    path = (base / project_id).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("项目路径越出 projects 目录")
    return path


def project_file(project_id: str, relative_path: str, *, archived: bool = False) -> Path:
    if Path(relative_path).is_absolute():
        raise ValueError("项目引用必须是相对路径")
    base = project_dir(project_id, archived=archived)
    path = (base / relative_path).resolve()
    if not path.is_relative_to(base):
        raise ValueError(f"项目引用越界：{relative_path}")
    return path
