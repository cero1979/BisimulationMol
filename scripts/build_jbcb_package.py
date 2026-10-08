"""Build and verify the flat, self-contained JBCB submission archive."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "jbcb"
FIGURES = ROOT / "figs"
SUBMISSION = ROOT / "submission_jbcb_r1_upload"
ARCHIVE_NAME = "JBCB-1505-R1-upload.zip"
MAIN_NAME = "main_jbcb_R1.tex"
PREVIEW = ROOT / "output" / "pdf" / "JBCB-1505-R1-upload-check.pdf"
BIBTEX_BLOCK = "\\bibliographystyle{ws-jbcb}\n\\bibliography{references_jbcb}"

SOURCE_FILES = ("main_jbcb.tex", "references_jbcb.bib")
RESOURCE_FILES = ("ws-jbcb.cls", "ws-jbcb.bst")
FIGURE_NAMES = {
    "Fig1.pdf": "R1_Fig1.pdf",
    "Fig3.pdf": "R1_Fig2.pdf",
    "Fig2.pdf": "R1_Fig3.pdf",
    "Fig8.pdf": "R1_Fig4.pdf",
    "FigS1a.pdf": "R1_Fig5.pdf",
    "FigS1b.pdf": "R1_Fig6.pdf",
}
PACKAGE_FILES = (MAIN_NAME, "ws-jbcb.cls", *FIGURE_NAMES.values())


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required file is missing: {path}")
    return path


def run_tex(command: list[str], directory: Path) -> None:
    environment = os.environ.copy()
    environment.setdefault("TZ", "UTC")
    completed = subprocess.run(
        command,
        cwd=directory,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("JBCB package compilation failed:\n" + completed.stdout)


def check_compile_log(directory: Path, stem: str) -> None:
    log = require(directory / f"{stem}.log").read_text(
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
    if re.search(r"(?:Citation|Reference) .* undefined", log):
        present.append("unresolved citation or reference")
    if present:
        raise RuntimeError("JBCB package log contains: " + ", ".join(present))
    require(directory / f"{stem}.pdf")


def prepare_upload_source(source: str, bibliography: str) -> str:
    """Embed the journal-formatted references and isolate revision filenames."""
    if source.count(BIBTEX_BLOCK) != 1:
        raise RuntimeError("Expected exactly one BibTeX block in main_jbcb.tex")
    if bibliography.count("\\begin{thebibliography}") != 1 or bibliography.count(
        "\\end{thebibliography}"
    ) != 1:
        raise RuntimeError("Invalid generated bibliography")
    source = source.replace(BIBTEX_BLOCK, bibliography.rstrip())
    source = re.sub(r"\\graphicspath\{[^\n]*\}", lambda _: r"\graphicspath{{./}}", source)
    for original, renamed in FIGURE_NAMES.items():
        token = "{" + original + "}"
        if source.count(token) != 1:
            raise RuntimeError(f"Expected exactly one figure inclusion: {original}")
        source = source.replace(token, "{" + renamed + "}")
    if re.search(r"\\(?:input|include|bibliography|bibliographystyle)\s*\{", source):
        raise RuntimeError("Upload source still needs an external TeX/bibliography file")
    return source


def build_package() -> Path:
    source = require(SOURCE / "main_jbcb.tex").read_text(encoding="utf-8")
    # Generate the bibliography from the canonical source with the official style.
    with tempfile.TemporaryDirectory(prefix="jbcb-bib-") as scratch:
        directory = Path(scratch)
        for name in SOURCE_FILES + RESOURCE_FILES:
            shutil.copy2(require(SOURCE / name), directory / name)
        for name in FIGURE_NAMES:
            shutil.copy2(require(FIGURES / name), directory / name)
        run_tex([
            "latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
            "main_jbcb.tex",
        ], directory)
        check_compile_log(directory, "main_jbcb")
        bibliography = require(directory / "main_jbcb.bbl").read_text(encoding="utf-8")
    upload_source = prepare_upload_source(source, bibliography)

    if SUBMISSION.is_symlink():
        raise RuntimeError(f"Refusing to replace symlink: {SUBMISSION}")
    if SUBMISSION.exists():
        shutil.rmtree(SUBMISSION)

    SUBMISSION.mkdir(parents=True)
    (SUBMISSION / MAIN_NAME).write_text(upload_source, encoding="utf-8")
    shutil.copy2(require(SOURCE / "ws-jbcb.cls"), SUBMISSION / "ws-jbcb.cls")
    for original, renamed in FIGURE_NAMES.items():
        shutil.copy2(require(FIGURES / original), SUBMISSION / renamed)

    archive_path = ROOT / ARCHIVE_NAME
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in PACKAGE_FILES:
            archive.write(require(SUBMISSION / name), arcname=name)

    # Compile the actual ZIP in an empty directory using pdflatex alone.
    with tempfile.TemporaryDirectory(prefix="jbcb-upload-") as scratch:
        directory = Path(scratch)
        with zipfile.ZipFile(archive_path) as archive:
            if set(archive.namelist()) != set(PACKAGE_FILES) or archive.testzip():
                raise RuntimeError("Invalid upload archive contents")
            archive.extractall(directory)
        for _ in range(3):
            run_tex([
                "pdflatex", "-interaction=nonstopmode", "-halt-on-error", MAIN_NAME,
            ], directory)
        check_compile_log(directory, Path(MAIN_NAME).stem)
        PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(directory / Path(MAIN_NAME).with_suffix(".pdf"), PREVIEW)
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
    print(f"Verified PDF: {PREVIEW}")
