"""Reproduce the PN-GDDA reference score with the official Holmes 1.1.1 JAR."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import pn_gdda  # noqa: E402


PROBE = ROOT / "scripts" / "HolmesPnGddaProbe.java"
DEFAULT_OUTPUT = ROOT / "results" / "holmes_pn_gdda_external_validation.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_jar(directory: Path) -> Path:
    archive = directory / "HolmesRelease_111.zip"
    urllib.request.urlretrieve(pn_gdda.HOLMES_111_URL, archive)
    with zipfile.ZipFile(archive) as bundle:
        member = "HolmesRelease/Holmes.jar"
        bundle.extract(member, directory)
    return directory / member


def validate_catalog(output: str) -> tuple[int, int]:
    pattern = re.compile(r"^catalog=(\d+);(\d+);([0-2,]+);([0-9:,]+)$")
    observed = []
    for line in output.splitlines():
        match = pattern.match(line)
        if match is None:
            continue
        place_count = int(match.group(1))
        transition_count = int(match.group(2))
        code = tuple(int(value) for value in match.group(3).split(","))
        slots = tuple(
            (int(slot), int(root))
            for slot, root in (
                item.split(":") for item in match.group(4).split(",")
            )
        )
        canonical, mapping = pn_gdda._canonical_code_and_mapping(
            place_count, transition_count, code
        )
        observed.append(
            ((place_count, transition_count, canonical), slots, mapping)
        )

    catalog = {
        entry.signature: entry for entry in pn_gdda.graphlet_catalog(True)
    }
    if len(observed) != len(catalog) or len({row[0] for row in observed}) != len(catalog):
        raise AssertionError(
            f"Holmes catalog has {len(observed)} rows and "
            f"{len({row[0] for row in observed})} unique signatures; expected 151"
        )

    all_slot_ids = []
    for signature, slots, mapping in observed:
        entry = catalog.get(signature)
        if entry is None:
            raise AssertionError(f"Holmes-only graphlet signature: {signature}")
        if len(slots) != len(entry.orbit_slots):
            raise AssertionError(
                f"Orbit-slot mismatch for {signature}: "
                f"Holmes={len(slots)}, Python={len(entry.orbit_slots)}"
            )
        place_count, transition_count, code = signature
        mathematical_orbits = pn_gdda._automorphism_orbits(
            place_count, transition_count, code
        )
        observed_orbits = []
        for global_slot, root in slots:
            canonical_root = mapping[root]
            observed_orbits.append(
                next(orbit for orbit in mathematical_orbits if canonical_root in orbit)
            )
            all_slot_ids.append(global_slot)
        if Counter(observed_orbits) != Counter(entry.orbit_slots):
            raise AssertionError(f"Orbit-slot membership mismatch for {signature}")

    if len(set(all_slot_ids)) != len(all_slot_ids):
        counts = Counter(all_slot_ids)
        duplicates = sorted(slot for slot, count in counts.items() if count > 1)
        raise AssertionError(f"Duplicate Holmes global orbit-slot IDs: {duplicates}")
    return len(observed), len(all_slot_ids)


def run_probe(jar: Path, directory: Path) -> tuple[int, float, int, int]:
    subprocess.run(
        ["javac", "-cp", str(jar), "-d", str(directory), str(PROBE)],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [
            "java",
            "-Djava.awt.headless=true",
            "-cp",
            os.pathsep.join((str(jar), str(directory))),
            "HolmesPnGddaProbe",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    orbit_match = re.search(r"^orbits=(\d+)$", completed.stdout, re.MULTILINE)
    score_match = re.search(
        r"^agreement=([0-9.]+)$", completed.stdout, re.MULTILINE
    )
    if orbit_match is None or score_match is None:
        raise RuntimeError(f"Unexpected Holmes output:\n{completed.stdout}")
    graphlet_count, catalog_slot_count = validate_catalog(completed.stdout)
    return (
        int(orbit_match.group(1)),
        float(score_match.group(1)),
        graphlet_count,
        catalog_slot_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jar",
        type=Path,
        help="Use an existing Holmes 1.1.1 JAR instead of downloading the archive.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="holmes-pn-gdda-") as temp:
        directory = Path(temp)
        jar = args.jar.resolve() if args.jar else download_jar(directory)
        observed_hash = sha256(jar)
        if observed_hash != pn_gdda.HOLMES_111_SHA256:
            raise ValueError(
                "Holmes JAR SHA-256 mismatch: "
                f"expected {pn_gdda.HOLMES_111_SHA256}, observed {observed_hash}"
            )
        orbit_count, holmes_score, graphlet_count, catalog_slot_count = run_probe(
            jar, directory
        )

    left, right = pn_gdda.holmes_reference_pair()
    python_score = pn_gdda.pn_gdda_similarity(left, right, True)
    payload = {
        "download_url": pn_gdda.HOLMES_111_URL,
        "holmes_version": "1.1.1",
        "jar_sha256": observed_hash,
        "holmes_orbit_slots": orbit_count,
        "holmes_graphlet_topologies": graphlet_count,
        "holmes_catalog_slots_verified": catalog_slot_count,
        "catalog_matches_python": graphlet_count == 151
        and catalog_slot_count == 592,
        "holmes_score": holmes_score,
        "independent_python_score": python_score,
        "absolute_score_difference": abs(holmes_score - python_score),
        "agreement_at_12_decimals": round(holmes_score, 12)
        == round(python_score, 12),
    }
    if (
        orbit_count != 592
        or not payload["catalog_matches_python"]
        or not payload["agreement_at_12_decimals"]
    ):
        raise AssertionError(f"PN-GDDA external validation failed: {payload}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
