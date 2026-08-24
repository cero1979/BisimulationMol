"""Build and verify the flat, self-contained JBCB submission archive."""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "jbcb"
FIGURES = ROOT / "figs"
SUBMISSION = ROOT / "submission_jbcb_revision"
ARCHIVE_NAME = "JBCB-1505-revised.zip"
GENERATED_BBL = "main_jbcb.bbl"
SUBMISSION_BBL = "bibliography_jbcb.bbl"

SOURCE_FILES = ("main_jbcb.tex", "references_jbcb.bib")
RESOURCE_FILES = ("ws-jbcb.cls", "ws-jbcb.bst")
FIGURE_FILES = (
    "Fig1.pdf",
    "Fig2.pdf",
    "Fig3.pdf",
    "Fig8.pdf",
    "FigS1a.pdf",
    "FigS1b.pdf",
)
BUILD_FILES = (
    "main_jbcb.aux",
    "main_jbcb.bbl",
    "main_jbcb.blg",
    "main_jbcb.fdb_latexmk",
    "main_jbcb.fls",
    "main_jbcb.log",
    "main_jbcb.out",
    "main_jbcb.pdf",
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


def prepare_editorial_manager_bibliography() -> None:
    """Replace the BibTeX call with a prebuilt BBL for the EM PDF builder."""
    generated = require(SUBMISSION / GENERATED_BBL)
    shutil.copy2(generated, SUBMISSION / SUBMISSION_BBL)

    manuscript = require(SUBMISSION / "main_jbcb.tex")
    source = manuscript.read_text(encoding="utf-8")
    bibtex_block = "\\bibliographystyle{ws-jbcb}\n\\bibliography{references_jbcb}"
    bbl_input = f"\\input{{{SUBMISSION_BBL}}}"
    if source.count(bibtex_block) != 1:
        raise RuntimeError("Expected exactly one BibTeX block in main_jbcb.tex")
    manuscript.write_text(source.replace(bibtex_block, bbl_input), encoding="utf-8")


def build_package() -> Path:
    if SUBMISSION.is_symlink():
        raise RuntimeError(f"Refusing to replace symlink: {SUBMISSION}")
    if SUBMISSION.exists():
        shutil.rmtree(SUBMISSION)

    SUBMISSION.mkdir(parents=True)
    for name in SOURCE_FILES + RESOURCE_FILES:
        shutil.copy2(require(SOURCE / name), SUBMISSION / name)
    for name in FIGURE_FILES:
        shutil.copy2(require(FIGURES / name), SUBMISSION / name)

    # First compile generates the journal-formatted bibliography.
    compile_clean_source()
    prepare_editorial_manager_bibliography()

    for name in BUILD_FILES:
        path = SUBMISSION / name
        if path.exists():
            path.unlink()

    # Verify the exact source that Editorial Manager will receive.
    compile_clean_source()

    for name in BUILD_FILES:
        path = SUBMISSION / name
        if path.exists():
            path.unlink()

    package_files = [
        SUBMISSION / "main_jbcb.tex",
        SUBMISSION / SUBMISSION_BBL,
        SUBMISSION / "references_jbcb.bib",
        *(SUBMISSION / name for name in RESOURCE_FILES),
        *(SUBMISSION / name for name in FIGURE_FILES),
    ]
    archive_path = ROOT / ARCHIVE_NAME
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
    nested = [name for name in names if "/" in name.rstrip("/")]
    if nested:
        raise RuntimeError("Editorial Manager rejects subfolders: " + ", ".join(nested))
    print(f"Built {archive}")
    print(f"Verified {len(names)} files: " + ", ".join(names))
