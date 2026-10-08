"""Build production PDFs and a flat archive without reassembling the R3 text."""

from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_jbcb_R3_package import MAIN, SUPPLEMENT, compile_master, validate_source

SOURCE = ROOT / "revision_R3"
OUTPUT = ROOT / "production_jbcb_R3"
ARCHIVE = ROOT / "JBCB-1505-R3-production.zip"
MASTERS = ("main_jbcb_R3.tex", "Supplementary_Validation_R3.tex")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUTPUT.mkdir(exist_ok=True)
    sources = sorted(set(MAIN + SUPPLEMENT))
    before = {name: digest(SOURCE / name) for name in sources}
    builds = {}
    for master in MASTERS:
        validate_source((SOURCE / master).read_text(), sources)
    with tempfile.TemporaryDirectory(prefix="jbcb-R3-production-") as temp:
        directory = Path(temp)
        for name in sources:
            shutil.copy2(SOURCE / name, directory / name)
        for master in MASTERS:
            warnings = compile_master(directory, master)
            if warnings:
                raise RuntimeError(f"{master}: {warnings}")
            pdf = Path(master).with_suffix(".pdf").name
            shutil.copy2(directory / pdf, SOURCE / pdf)
            shutil.copy2(directory / pdf, OUTPUT / pdf)
            log = Path(master).with_suffix(".log")
            shutil.copy2(directory / log, OUTPUT / log)
            builds[master] = {"engine": "pdflatex", "passes": 3,
                              "clean_build": True, "warnings": warnings}
        for name in sources:
            shutil.copy2(directory / name, OUTPUT / name)

    assert before == {name: digest(SOURCE / name) for name in sources}
    files = sources + [Path(name).with_suffix(".pdf").name for name in MASTERS]
    files += ["author_biography.txt", "PRODUCTION_README.txt"]
    assert len(files) == len(set(files))
    manifest = {name: digest(OUTPUT / name) for name in files}
    with zipfile.ZipFile(ARCHIVE, "w") as archive:
        for name in files:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (OUTPUT / name).read_bytes())

    # Rebuild from the delivered archive with no packaged PDFs or auxiliaries.
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        assert all("/" not in name and "\\" not in name for name in archive.namelist())
        assert all(hashlib.sha256(archive.read(name)).hexdigest() == value
                   for name, value in manifest.items())
        with tempfile.TemporaryDirectory(prefix="jbcb-R3-production-check-") as temp:
            directory = Path(temp)
            archive.extractall(directory)
            for master in MASTERS:
                (directory / Path(master).with_suffix(".pdf")).unlink()
                assert compile_master(directory, master) == []

    report = {"archive": ARCHIVE.name, "sha256": digest(ARCHIVE),
              "flat": True, "source_files_unchanged": True,
              "archive_clean_rebuild_passed": True, "builds": builds,
              "files_sha256": manifest}
    (OUTPUT / "production_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
