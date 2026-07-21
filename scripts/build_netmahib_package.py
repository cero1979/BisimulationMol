"""Build a flat, source-only LaTeX archive for NetMAHIB submission."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "netmahib"
FIGURES = ROOT / "figs"
SUBMISSION = ROOT / "submission"
PACKAGE = SUBMISSION / "netmahib_latex_flat"
ARCHIVE = SUBMISSION / "netmahib_latex_flat.zip"
REPRO_ARCHIVE = SUBMISSION / "netmahib_reproducibility.zip"

SOURCE_FILES = (
    "main.tex",
    "sn-jnl.cls",
    "sn-mathphys-ay.bst",
    "references.bib",
    "main.bbl",
)
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

REPRO_FILES = (
    "Makefile",
    "requirements.txt",
    "environment.yml",
    "environment-hpn.yml",
    "README.md",
    "REPRODUCIBILITY.md",
    "CITATION.cff",
    "LICENSE",
    "make_figures.py",
)
REPRO_DIRS = (
    "src",
    "scripts",
    "tests",
    "data/public_models",
    "data/hpn_dream",
    "results",
    "notebooks",
    "paper/netmahib",
    ".github/workflows",
)


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(
            f"Required file is missing: {path}. Run 'make figures manuscript' first."
        )
    return path


def build_reproducibility_archive() -> Path:
    if REPRO_ARCHIVE.exists():
        REPRO_ARCHIVE.unlink()
    excluded_suffixes = {".pyc", ".pdf", ".aux", ".log", ".blg", ".fls"}
    with zipfile.ZipFile(
        REPRO_ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for name in REPRO_FILES:
            path = require(ROOT / name)
            archive.write(path, arcname=name)
        for directory in REPRO_DIRS:
            base = ROOT / directory
            if not base.is_dir():
                raise FileNotFoundError(f"Required directory is missing: {base}")
            for path in sorted(base.rglob("*")):
                if (
                    not path.is_file()
                    or "__pycache__" in path.parts
                    or ".ipynb_checkpoints" in path.parts
                    or path.name == ".DS_Store"
                    or path.suffix in excluded_suffixes
                ):
                    continue
                archive.write(path, arcname=path.relative_to(ROOT))
    return REPRO_ARCHIVE


def build_package() -> tuple[Path, Path]:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True)

    for name in SOURCE_FILES:
        shutil.copy2(require(SOURCE / name), PACKAGE / name)
    for name in FIGURE_FILES:
        shutil.copy2(require(FIGURES / name), PACKAGE / name)

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE.iterdir()):
            archive.write(path, arcname=path.name)

    return ARCHIVE, build_reproducibility_archive()


if __name__ == "__main__":
    archive, reproducibility_archive = build_package()
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
    print(f"Built {archive}")
    print("Contents: " + ", ".join(names))
    with zipfile.ZipFile(reproducibility_archive) as package:
        reproducibility_names = package.namelist()
    print(f"Built {reproducibility_archive}")
    print(f"Reproducibility files: {len(reproducibility_names)}")
