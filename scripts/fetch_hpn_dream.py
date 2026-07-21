#!/usr/bin/env python3
"""Fetch the hash-pinned HPN-DREAM/CASPOTS validation artifacts.

The files were published in the CASPOTS repository and later removed from its
default branch.  Raw URLs therefore point to the first public commit that
contains the model families, learning data and held-out mTOR-inhibitor tests.
"""

from __future__ import annotations

import hashlib
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "data" / "hpn_dream"
REPOSITORY = "https://raw.githubusercontent.com/misbahch6/caspo-ts"
COMMIT = "95e3c74ed0165110b12de66634a8a9ca7ff515e8"


@dataclass(frozen=True)
class Artifact:
    destination: str
    source_path: str
    sha256: str

    @property
    def url(self) -> str:
        encoded = urllib.parse.quote(self.source_path, safe="/")
        return f"{REPOSITORY}/{COMMIT}/{encoded}"


ARTIFACTS = (
    Artifact(
        "merged_pkn.sif",
        "datasets/Dream8/merge_hpn_cmpr_CS.sif",
        "9eb1266e6f70764986afffc6a2728adcd6fd17d5cd625526d8601cab5c7adec3",
    ),
    Artifact(
        "BT20_family.csv",
        "datasets/Dream8/BT20-BNs-CS-CO-Valid.csv",
        "c1fb52005641d705b81aec28983bb53c2dab1969c4c53a2bd24397fe5f45cd6e",
    ),
    Artifact(
        "BT549_family.csv",
        "datasets/Dream8/Valid Boolean Networks for Dream 8 /Merged 3 PKNs/BT549-BNs-CS-Valid.csv",
        "d0912091719881cc3c1a271d7454ddd2f1f19b39f9f7a8fa75b707e4c13c2a7c",
    ),
    Artifact(
        "MCF7_family.csv",
        "datasets/Dream8/MCF7-BNs-CS-Valid.csv",
        "9f41c4020dd0f4d589dfc35af4052f23a7abde8f8ea4dc3346ab1cbcc9626feb",
    ),
    Artifact(
        "BT20_learning.csv",
        "datasets/Dream8/BT20Refined-remove-ready.csv",
        "d8e7195b2db52c24829bb8662d6015140f7147b7606fc76dfe613f2e42d3305e",
    ),
    Artifact(
        "BT549_learning.csv",
        "datasets/Dream8/BT549Refined-remove-ready.csv",
        "a5ca48bf621cf0d9f912e25ff75fd9e96d40336882f895ae10009f0750eb0725",
    ),
    Artifact(
        "MCF7_learning.csv",
        "datasets/Dream8/MCF715expOnly.csv",
        "46dee96500d9ceca38f30c132be2f0fb03dbebac49309f26d85634ee9fd45c2d",
    ),
    Artifact(
        "BT20_test.csv",
        "datasets/Dream8/MD-BT20_main_test_f1.csv",
        "19861374078c538e6add650dce0c47f85282747a46316da9feeb25828a4ee857",
    ),
    Artifact(
        "BT549_test.csv",
        "datasets/Dream8/MD-BT549_main_test_f1.csv",
        "bf2fd40cad5f8aa9b42efc56dca245eee48afe7117e705a4daa5bca4d35c9559",
    ),
    Artifact(
        "MCF7_test.csv",
        "datasets/Dream8/MD-MCF7_main_test_f1.csv",
        "b81175a4d97689ee6f8e1d002e92ad7cf04b4067838e8d56ca467826c2458a5c",
    ),
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(artifact: Artifact) -> Path:
    destination = DESTINATION / artifact.destination
    if destination.is_file():
        payload = destination.read_bytes()
        if digest(payload) == artifact.sha256:
            print(f"verified {destination.relative_to(ROOT)}")
            return destination

    request = urllib.request.Request(
        artifact.url, headers={"User-Agent": "BisimulationMol-reproducibility"}
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()
    observed = digest(payload)
    if observed != artifact.sha256:
        raise RuntimeError(
            f"SHA-256 mismatch for {artifact.destination}: "
            f"expected {artifact.sha256}, observed {observed}"
        )
    destination.write_bytes(payload)
    print(f"downloaded {destination.relative_to(ROOT)}")
    return destination


def main() -> int:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    try:
        for artifact in ARTIFACTS:
            fetch(artifact)
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
