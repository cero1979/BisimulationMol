"""Build and verify the self-contained JBCB submission archive."""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "jbcb"
FIGURES = ROOT / "figs"
SUBMISSION = ROOT / "submission_jbcb"
ARCHIVE_NAME = "JBCB_submission.zip"

SOURCE_FILES = ("main_jbcb.tex", "references_jbcb.bib")
RESOURCE_FILES = ("ws-jbcb.cls", "ws-jbcb.bst")
FIGURE_FILES = ("Fig1.pdf", "Fig2a.pdf", "Fig2b.pdf", "Fig3.pdf", "Fig8.pdf")
BUILD_FILES = (
    "main_jbcb.aux",
    "main_jbcb.bbl",
    "main_jbcb.blg",
    "main_jbcb.fdb_latexmk",
    "main_jbcb.fls",
    "main_jbcb.log",
    "main_jbcb.out",
    "main_jbcb.synctex.gz",
)


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required file is missing: {path}")
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
            "main_jbcb.tex",
        ],
        cwd=SUBMISSION,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("JBCB package compilation failed:\n" + completed.stdout)

    log = require(SUBMISSION / "main_jbcb.log").read_text(
        encoding="utf-8", errors="replace"
    )
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
        raise RuntimeError("JBCB package log contains: " + ", ".join(present))
    require(SUBMISSION / "main_jbcb.pdf")


def build_package() -> Path:
    if SUBMISSION.is_symlink():
        raise RuntimeError(f"Refusing to replace symlink: {SUBMISSION}")
    if SUBMISSION.exists():
        shutil.rmtree(SUBMISSION)

    (SUBMISSION / "figures").mkdir(parents=True)
    for name in SOURCE_FILES + RESOURCE_FILES:
        shutil.copy2(require(SOURCE / name), SUBMISSION / name)
    for name in FIGURE_FILES:
        shutil.copy2(require(FIGURES / name), SUBMISSION / "figures" / name)

    compile_clean_source()

    for name in BUILD_FILES:
        path = SUBMISSION / name
        if path.exists():
            path.unlink()

    package_files = [
        *(SUBMISSION / name for name in SOURCE_FILES + RESOURCE_FILES),
        *(SUBMISSION / "figures" / name for name in FIGURE_FILES),
        SUBMISSION / "main_jbcb.pdf",
    ]
    archive_path = SUBMISSION / ARCHIVE_NAME
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
