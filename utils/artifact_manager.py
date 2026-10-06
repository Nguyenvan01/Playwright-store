# QUẢN LÝ BẰNG CHỨNG: tập trung tên thư mục và tên file an toàn.
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from uuid import uuid4


@dataclass(frozen=True)
class ArtifactLayout:
    root: Path
    run_id: str
    logs: Path
    screenshots: Path
    page_sources: Path
    traces: Path
    junit: Path
    allure_results: Path


def create_artifact_layout(root, run_id=None):
    run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(root)
    layout = ArtifactLayout(
        root=base,
        run_id=run_id,
        logs=base / "logs",
        screenshots=base / "screenshots" / run_id,
        page_sources=base / "page_sources" / run_id,
        traces=base / "traces" / run_id,
        junit=base / "junit",
        allure_results=base / "allure-results",
    )
    for directory in (
        layout.logs,
        layout.screenshots,
        layout.page_sources,
        layout.traces,
        layout.junit,
        layout.allure_results,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return layout


def safe_artifact_name(node_name):
    clean = re.sub(r"[^A-Za-z0-9_.-]", "_", node_name).strip("._")[:100]
    return f"{clean or 'test'}_{uuid4().hex[:8]}"
