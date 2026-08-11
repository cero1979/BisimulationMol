"""Build and compile the self-contained JMCS submission archive."""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "jmcs"
FIGURES = ROOT / "figs"
SUBMISSION = ROOT / "submission_jmcs"
ARCHIVE_NAME = "JMCS_submission.zip"

SOURCE_FILES = ("main.tex", "references_jmcs.tex")
RESOURCE_FILES = ("ISRP.cls", "jmcs.jpg")
FIGURE_FILES = (
    "Fig1.pdf",
    "Fig2a.pdf",
    "Fig2b.pdf",
    "Fig3.pdf",
    "Fig4.pdf",
    "Fig5a.pdf",
    "Fig5b.pdf",
    "Fig6a.pdf",
    "Fig6b.pdf",
    "Fig7a.pdf",
    "Fig7b.pdf",
    "Fig8.pdf",
)
BUILD_FILES = (
    "main.aux",
    "main.bbl",
    "main.blg",
    "main.brf",
    "main.fdb_latexmk",
    "main.fls",
    "main.log",
    "main.out",
    "main.spl",
    "main.synctex.gz",
)


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(
            f"Required file is missing: {path}. Run 'make verify' first."
        )
    return path


def compile_clean_source() -> None:
    environment = os.environ.copy()
    environment.setdefault("TZ", "UTC")
    completed = subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "main.tex",
        ],
        cwd=SUBMISSION,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("JMCS package compilation failed:\n" + completed.stdout)

    log = require(SUBMISSION / "main.log").read_text(encoding="utf-8", errors="replace")
    forbidden = (
        "LaTeX Error:",
        "Emergency stop",
        "There were undefined references",
        "There were undefined citations",
        "Overfull \\hbox",
        "Underfull \\hbox",
    )
    present = [marker for marker in forbidden if marker in log]
    if present:
        raise RuntimeError("JMCS package log contains: " + ", ".join(present))
    require(SUBMISSION / "main.pdf")


def build_package() -> Path:
    if SUBMISSION.is_symlink():
        raise RuntimeError(f"Refusing to replace symlink: {SUBMISSION}")
    if SUBMISSION.exists():
        shutil.rmtree(SUBMISSION)

    (SUBMISSION / "resources").mkdir(parents=True)
    (SUBMISSION / "figures").mkdir()

    for name in SOURCE_FILES:
        shutil.copy2(require(SOURCE / name), SUBMISSION / name)
    for name in RESOURCE_FILES:
        shutil.copy2(require(SOURCE / "resources" / name), SUBMISSION / "resources" / name)
    for name in FIGURE_FILES:
        shutil.copy2(require(FIGURES / name), SUBMISSION / "figures" / name)

    compile_clean_source()

    for name in BUILD_FILES:
        path = SUBMISSION / name
        if path.exists():
            path.unlink()

    archive_path = SUBMISSION / ARCHIVE_NAME
    package_files = [
        SUBMISSION / "main.tex",
        SUBMISSION / "references_jmcs.tex",
        SUBMISSION / "main.pdf",
        *(SUBMISSION / "resources" / name for name in RESOURCE_FILES),
        *(SUBMISSION / "figures" / name for name in FIGURE_FILES),
    ]
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in package_files:
            archive.write(require(path), arcname=path.relative_to(SUBMISSION))
    return archive_path


if __name__ == "__main__":
    archive = build_package()
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        bad = package.testzip()
    if bad is not None:
        raise RuntimeError(f"Corrupt ZIP member: {bad}")
    print(f"Built {archive}")
    print(f"Verified {len(names)} files: " + ", ".join(names))
