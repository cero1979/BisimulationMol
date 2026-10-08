"""Compile the accepted Journal sources and validate a flat, complete archive."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Journal"
MASTERS = ("main.tex", "supplement.tex")
SOURCES = (*MASTERS, "ws-jbcb.cls", *(f"Fig{i}.pdf" for i in range(1, 5)),
           "SFig1.pdf", "SFig2.pdf")


def validate_source(source, available):
    if re.search(r"\\(?:input|include|bibliography|bibliographystyle)\s*\{", source):
        raise ValueError("An external TeX/bibliography dependency remains")
    if source.count(r"\begin{thebibliography}") != 1:
        raise ValueError("Expected one inline bibliography")
    figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", source)
    if not set(figures) <= set(available):
        raise ValueError(f"Missing artwork: {set(figures) - set(available)}")
    return figures


def compile_master(directory, master):
    for _ in range(3):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", master],
            cwd=directory, text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(result.stdout[-8000:] + result.stderr)
    log = (directory / Path(master).with_suffix(".log")).read_text(errors="replace")
    problems = [line for line in log.splitlines() if re.search(
        r"LaTeX Error|Emergency stop|undefined|Overfull \\[hv]box|Underfull \\hbox|Rerun to get|Warning", line
    )]
    if problems:
        raise RuntimeError("\n".join(problems))


def write_archive(path, include_pdfs=True):
    names = list(SOURCES)
    if include_pdfs:
        names += [Path(name).with_suffix(".pdf").name for name in MASTERS]
    for master in MASTERS:
        validate_source((SOURCE / master).read_text(), names)
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (SOURCE / name).read_bytes())
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        assert all("/" not in name and "\\" not in name for name in archive.namelist())
        for name in names:
            assert archive.read(name) == (SOURCE / name).read_bytes()
    return names


def main():
    before = {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in SOURCES}
    for master in MASTERS:
        validate_source((SOURCE / master).read_text(), SOURCES)
    with tempfile.TemporaryDirectory(prefix="jbcb-journal-build-") as temp:
        directory = Path(temp)
        for name in SOURCES:
            shutil.copy2(SOURCE / name, directory / name)
        for master in MASTERS:
            compile_master(directory, master)
            pdf = Path(master).with_suffix(".pdf")
            shutil.copy2(directory / pdf, SOURCE / pdf)
    assert before == {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in SOURCES}
    archive_path = SOURCE / "Journal.zip"
    names = write_archive(archive_path)
    with tempfile.TemporaryDirectory(prefix="jbcb-journal-extracted-") as temp:
        directory = Path(temp)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(directory)
        for master in MASTERS:
            (directory / Path(master).with_suffix(".pdf")).unlink()
            compile_master(directory, master)
    report = {
        "journal": "Journal of Bioinformatics and Computational Biology",
        "archive": archive_path.name,
        "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "engine": "pdflatex", "passes_per_master": 3,
        "clean_source_build": True, "clean_extracted_archive_build": True,
        "sources_unchanged": True, "warnings": [],
        "files_sha256": {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in names},
    }
    (SOURCE / "build_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
