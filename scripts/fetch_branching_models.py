"""Fetch the pinned model and freeze configuration before relation computation."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.death_receptor_analysis import SOURCE, validate_download, configuration, config_hash


def main():
    if not SOURCE.path.exists():
        with urlopen(SOURCE.url, timeout=60) as stream:
            data = stream.read()
        validate_download(data)
        SOURCE.path.parent.mkdir(parents=True, exist_ok=True)
        SOURCE.path.write_bytes(data)
    validate_download(SOURCE.path.read_bytes())
    config = configuration()
    target = ROOT / 'results/branching_case_preregistration.json'
    if target.exists():
        frozen = json.loads(target.read_text())
        if frozen['configuration'] != config:
            raise ValueError('Frozen configuration differs; an explicit amendment is required')
    else:
        frozen = {'record_type': 'local prospective configuration, not external registration',
                  'created_utc': datetime.now(timezone.utc).isoformat(),
                  'formal_results_computed_before_record': False,
                  'configuration_sha256': config_hash(config), 'configuration': config}
        target.write_text(json.dumps(frozen, indent=2, sort_keys=True) + '\n')
    interface = dict(config['interface'], source=config['source'],
                     configuration_sha256=frozen['configuration_sha256'],
                     created_utc=frozen['created_utc'])
    (ROOT / 'results/death_receptor_interface.json').write_text(
        json.dumps(interface, indent=2, sort_keys=True) + '\n')
    print('Verified source and frozen configuration:', frozen['configuration_sha256'])


if __name__ == '__main__':
    main()
