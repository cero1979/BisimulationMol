"""Build flat R2 archives and verify every master in an empty directory."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "revision_R2"
MAIN = ["main_jbcb_R2.tex", "ws-jbcb.cls"] + [f"R2_Fig{i}.pdf" for i in range(1, 5)]
SUPPLEMENT = ["Supplementary_Validation_R2.tex", "ws-jbcb.cls", "R2_SFig1.pdf", "R2_SFig2.pdf"]


def validate_source(source, available):
    if re.search(r"\\(?:input|include|bibliography|bibliographystyle)\s*\{", source):
        raise ValueError("An external TeX/bibliography dependency remains")
    if source.count(r"\begin{thebibliography}") != 1:
        raise ValueError("Expected one inline bibliography")
    figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", source)
    if not set(figures) <= set(available):
        raise ValueError(f"Missing artwork: {set(figures) - set(available)}")
    return figures


def check_log(path):
    log = path.read_text(errors="replace")
    problems = [line for line in log.splitlines()
                if re.search(r"LaTeX Error|Emergency stop|undefined|Overfull \\[hv]box|Underfull \\hbox|Rerun to get", line)]
    if problems:
        raise RuntimeError("\n".join(problems))
    return [line for line in log.splitlines() if "Warning" in line]


def compile_master(directory, master):
    for _ in range(3):
        command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", master]
        result = subprocess.run(command, cwd=directory, text=True, capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stdout[-8000:] + result.stderr)
    return check_log(directory / Path(master).with_suffix(".log"))


def build_archive(name, files, masters):
    archive = ROOT / name
    for master in masters:
        validate_source((SOURCE / master).read_text(), files)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for name in files:
            # Fixed metadata makes identical content reproducible byte-for-byte.
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            handle.writestr(info, (SOURCE / name).read_bytes())
    report = {"archive": archive.name, "files": files, "masters": {}, "flat": True}
    with tempfile.TemporaryDirectory(prefix="jbcb-R2-clean-") as temp:
        directory = Path(temp)
        with zipfile.ZipFile(archive) as handle:
            assert handle.testzip() is None
            assert len(handle.namelist()) == len(set(handle.namelist()))
            assert all("/" not in name and "\\" not in name for name in handle.namelist())
            handle.extractall(directory)
        for master in masters:
            warnings = compile_master(directory, master)
            pdf = Path(master).with_suffix(".pdf")
            shutil.copy2(directory / pdf, SOURCE / pdf)
            (SOURCE / (Path(master).stem + "_clean_build.log")).write_text(
                (directory / Path(master).with_suffix(".log")).read_text())
            report["masters"][master] = {"three_pdflatex_passes": True, "bibtex_used": False,
                                         "cached_auxiliaries_used": False, "warnings": warnings}
    report["sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    return report


def main():
    reports = [
        build_archive("JBCB-1505-R2.zip", MAIN + [f for f in SUPPLEMENT if f not in MAIN],
                      ["main_jbcb_R2.tex", "Supplementary_Validation_R2.tex"]),
        build_archive("JBCB-1505-R2-manuscript-only.zip", MAIN, ["main_jbcb_R2.tex"]),
        build_archive("JBCB-1505-R2-supplement.zip", SUPPLEMENT, ["Supplementary_Validation_R2.tex"]),
    ]
    compile_master(SOURCE, "response_to_reviewer_R2.tex")
    (SOURCE / "package_validation_R2.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
