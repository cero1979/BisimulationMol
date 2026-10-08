"""Check corrected R3 outputs and refresh document/notebook audit metadata."""
import hashlib
import json
from pathlib import Path
import re
import zipfile
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'revision_R3'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')


def main():
    notebook = ROOT / 'notebooks/metodologia_multiescala.ipynb'
    nb = json.loads(notebook.read_text())
    codes = [c for c in nb['cells'] if c['cell_type'] == 'code']
    errors = [o for c in codes for o in c.get('outputs', []) if o.get('output_type') == 'error']
    assert not errors and all(c['execution_count'] is not None for c in codes)
    stale = r'global sustained (?:weak-)?trace (?:equivalence|equality)\s+(?:is|remains)\s+(?:computationally\s+)?unresolved'
    for cell in nb['cells']:
        assert not re.search(stale, ''.join(cell['source']), re.I)
    save('notebook_execution_R3.json', dict(cells=len(nb['cells']),code_cells=len(codes),
         executed=len(codes),errors=len(errors),sha256=digest(notebook)))

    result = json.loads((ROOT / 'results/death_receptor_sustained_comparison.json').read_text())
    assert result['trace_analysis']['exact_trace_equal'] is False
    assert result['weak_simulations']['left_simulated_by_right'] is False
    assert result['weak_simulations']['right_simulated_by_left'] is None
    assert result['weak_bisimilar'] is False
    assert json.loads((ROOT / 'results/death_receptor_sustained_external_word.json').read_text())['confirmed']

    layouts, sources = [], {}
    for stem in ('main_jbcb_R3', 'Supplementary_Validation_R3', 'response_to_reviewer_R3'):
        text = (OUT / (stem + '.tex')).read_text()
        assert not re.search(stale, text, re.I)
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        missing = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text)) - set(labels)
        assert not missing and len(labels) == len(set(labels))
        citations = []
        for group in re.findall(r'\\cite\{([^}]+)\}', text):
            for key in group.split(','):
                key = key.strip()
                if key not in citations:
                    citations.append(key)
        bibliography = re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}', text)
        assert citations == bibliography
        sources[stem + '.tex'] = dict(
            figures=re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', text),
            references=len(bibliography),unresolved_labels=sorted(missing),citation_order_correct=True)
        bad_glyphs, unresolved = [], []
        path = OUT / (stem + '.pdf')
        with pdfplumber.open(path) as document:
            for number, page in enumerate(document.pages, 1):
                content = page.extract_text() or ''
                if '??' in content:
                    unresolved.append(number)
                if any(c['x0'] < -1 or c['x1'] > page.width + 1 or c['top'] < -1
                       or c['bottom'] > page.height + 1 for c in page.chars):
                    bad_glyphs.append(number)
            layouts.append(dict(file=path.name,pages=len(document.pages),
                                off_page_glyphs=bad_glyphs,unresolved_pages=unresolved,sha256=digest(path)))
        assert not bad_glyphs and not unresolved
    save('pdf_layout_check_R3.json', layouts)

    packages = json.loads((OUT / 'package_validation_R3.json').read_text())
    for record in packages['archives']:
        path = ROOT / record['archive']
        assert digest(path) == record['sha256']
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            assert archive.namelist() == record['files']
            for name in archive.namelist():
                assert '/' not in name and '\\' not in name
                assert archive.read(name) == (OUT / name).read_bytes()
    sources['flat_archive_hashes_valid'] = True
    save('cross_artifact_check_R3.json', sources)

    before_path = ROOT / 'tmp/R3/correction_before_notebook.json'
    if before_path.is_file():
        before = json.loads(before_path.read_text())
        after = {p:digest(ROOT / p) for p in before}
        changed = [p for p in before if before[p] != after[p]]
        assert not changed, changed
        save('reproducibility_check_R3.json', dict(
            configuration_sha256=result['configuration_sha256'],
            command='python scripts/run_branching_cases.py; repeated by executed notebook',
            deterministic_files_checked=len(before),identical=True,changed=changed,sha256=after))
    print(json.dumps({'pdfs':layouts,'notebook_code_cells':len(codes),'all_checks_passed':True},indent=2))


if __name__ == '__main__':
    main()
