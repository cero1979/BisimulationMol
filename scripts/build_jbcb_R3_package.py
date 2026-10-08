"""Clean-build every R3 master and assemble deterministic flat submission files."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build_jbcb_R2_package import compile_master,validate_source
SOURCE=ROOT/'revision_R3'
MAIN=['main_jbcb_R3.tex','ws-jbcb.cls']+[f'R3_Fig{i}.pdf' for i in range(1,5)]
SUPPLEMENT=['Supplementary_Validation_R3.tex','ws-jbcb.cls','R3_SFig1.pdf','R3_SFig2.pdf']


def build_reproducibility_archive(path):
    files = [ROOT/name for name in ('README.md', 'REPRODUCIBILITY.md', 'requirements.txt',
             'Makefile', 'LICENSE', 'CITATION.cff', 'environment-hpn.yml', 'make_figures.py',
             'submission_jbcb_revision/bibliography_jbcb.bbl')]
    suffixes = {'.py', '.ipynb', '.json', '.csv', '.tsv', '.tex', '.bib', '.bst',
                '.cls', '.pdf', '.md', '.xml', '.sbml', '.zginml', '.sif', '.txt',
                '.bnet', '.ginml', '.csv.gz', '.java', '.yml', '.yaml'}
    for name in ('src', 'scripts', 'tests', 'data', 'results', 'notebooks', 'tools',
                 'revision_R2', 'revision_R3', 'paper/jbcb'):
        for file in (ROOT/name).rglob('*'):
            if (file.is_file() and file.suffix in suffixes
                    and not {'__pycache__', '.ipynb_checkpoints', 'literature'} & set(file.parts)
                    and file.name not in {'reproducibility_archive_R3.json',
                                          'portable_archive_check_R3.json'}):
                files.append(file)
    files = sorted(set(files))
    manifest = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with zipfile.ZipFile(path, 'w') as archive:
        for file in files:
            info=zipfile.ZipInfo(str(file.relative_to(ROOT)),date_time=(2026,9,23,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,file.read_bytes())
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==digest
                   for name,digest in manifest.items())
    return {'archive':path.name,'purpose':'code/data supplement, not a LaTeX upload',
            'files':len(files),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'file_sha256':manifest}


def archive(name,files):
    assert len(files)==len(set(files)) and all('/' not in f and '\\' not in f for f in files)
    path=ROOT/name
    with zipfile.ZipFile(path,'w') as z:
        for filename in files:
            info=zipfile.ZipInfo(filename,date_time=(2026,9,23,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,(SOURCE/filename).read_bytes())
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert all(z.read(f)==(SOURCE/f).read_bytes() for f in files)
    return {'archive':name,'files':files,'flat':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    reports=[]
    for master,files in [('main_jbcb_R3.tex',MAIN),('Supplementary_Validation_R3.tex',SUPPLEMENT),
                         ('response_to_reviewer_R3.tex',['response_to_reviewer_R3.tex'])]:
        if master!='response_to_reviewer_R3.tex':
            validate_source((SOURCE/master).read_text(),files)
        with tempfile.TemporaryDirectory(prefix='jbcb-R3-clean-') as temp:
            directory=Path(temp)
            for f in files:
                shutil.copy2(SOURCE/f,directory/f)
            warnings=compile_master(directory,master)
            stem=Path(master).stem
            shutil.copy2(directory/(stem+'.pdf'),SOURCE/(stem+'.pdf'))
            shutil.copy2(directory/(stem+'.log'),SOURCE/(stem+'_clean_build.log'))
            reports.append({'master':master,'clean_directory':True,'passes':3,
                            'external_bibliography':False,'warnings':warnings})
    archives=[archive('JBCB-1505-R3-manuscript-only.zip',MAIN),
              archive('JBCB-1505-R3-supplement.zip',SUPPLEMENT),
              archive('JBCB-1505-R3.zip',MAIN+['Supplementary_Validation_R3.pdf','response_to_reviewer_R3.pdf'])]
    report={'builds':reports,'archives':archives}
    (SOURCE/'package_validation_R3.json').write_text(json.dumps(report,indent=2)+'\n')
    reproduction=build_reproducibility_archive(ROOT/'JBCB-1505-R3-reproducibility.zip')
    (SOURCE/'reproducibility_archive_R3.json').write_text(json.dumps(reproduction,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
