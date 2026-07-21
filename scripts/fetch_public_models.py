"""Download and verify the two GINsim models used for external validation."""

from __future__ import annotations

import sys
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import public_validation as pv  # noqa: E402


def fetch() -> None:
    pv.PUBLIC_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for source in pv.PUBLIC_MODEL_SOURCES:
        if source.path.is_file() and pv.sha256_file(source.path) == source.sha256:
            print(f"Verified existing {source.filename}")
            continue
        with tempfile.NamedTemporaryFile(
            dir=pv.PUBLIC_MODEL_DIR, prefix=source.filename + ".", delete=False
        ) as handle:
            temporary = Path(handle.name)
            with urllib.request.urlopen(source.url, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    handle.write(chunk)
        actual = pv.sha256_file(temporary)
        if actual != source.sha256:
            temporary.unlink(missing_ok=True)
            raise ValueError(
                f"SHA-256 mismatch for {source.filename}: {actual} != {source.sha256}"
            )
        temporary.replace(source.path)
        print(f"Downloaded and verified {source.filename}")


if __name__ == "__main__":
    fetch()
