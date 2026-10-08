"""Bounded external full-graph checks; timeouts are inconclusive, never false."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.public_validation import find_ltscompare,mcrl2_version,sha256_file,write_aut
from src.death_receptor_analysis import (load_variants,regulatory_dependencies,
    OBSERVABLES,SUSTAINED_COUNTEREXAMPLE)
from src.compact_execution import compact_generate
from src.concurrent_biomodels import LTS


def check_sustained_word():
    binary=find_ltscompare()
    report={'version':mcrl2_version(binary),'word':list(SUSTAINED_COUNTEREXAMPLE),
            'scope':'regenerated hidden-sink quotients; weak properties preserved', 'checks':[]}
    target=ROOT/'results/death_receptor_sustained_external_word.json'
    with tempfile.TemporaryDirectory(prefix='jbcb-sustained-word-') as temp:
        directory=Path(temp)
        word=directory/'word.aut'
        write_aut(LTS('prefix-language',[str(i) for i in range(len(SUSTAINED_COUNTEREXAMPLE)+1)],
                      0,[(i,a,i+1) for i,a in enumerate(SUSTAINED_COUNTEREXAMPLE)]),word)
        for model,expected in zip(load_variants(),(True,False)):
            execution=compact_generate(model,OBSERVABLES,regulatory_dependencies(),
                                       omit_sinks=('NonACD','Apoptosis','Survival'))
            path=directory/'model.aut'
            execution.write_aut(path)
            row={'model':model.name,'expected':expected,'input_sha256':sha256_file(path),
                 'timeout_seconds':180,'preorder':'weak-trace-ac','strategy':'breadth'}
            del execution
            command=[str(binary),'--tau=tau','--preorder=weak-trace-ac',
                     '--strategy=breadth',str(word),str(path)]
            try:
                check=subprocess.run(command,text=True,capture_output=True,timeout=180)
                words=check.stdout.split()
                if check.returncode or not words or words[-1] not in ('true','false'):
                    raise RuntimeError(check.stderr)
                value=words[-1]=='true'
                if value is not expected:
                    raise AssertionError((model.name,value,expected))
                row.update(status='complete',value=value)
            except subprocess.TimeoutExpired:
                row.update(status='inconclusive',value=None,reason='180-second limit')
            report['checks'].append(row)
            print(model.name,row,flush=True)
    report['confirmed']=all(r['value'] is r['expected'] for r in report['checks'])
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


def main():
    binary=find_ltscompare()
    report={'version':mcrl2_version(binary),'scope':'hidden-sink quotient; weak relations are preserved, strong is quotient-specific','checks':[]}
    target=ROOT/'results/death_receptor_external_global.json'
    for protocol in ('sustained','withdrawal'):
        paths=[ROOT/'tmp/Journal'/f'{side}-{protocol}.aut' for side in ('plus','minus')]
        hashes=[sha256_file(p) for p in paths]
        for equivalence in ('bisim','weak-bisim','weak-trace'):
            command=[str(binary),'--tau=tau',f'--equivalence={equivalence}',*map(str,paths)]
            row={'protocol':protocol,'equivalence':equivalence,'input_sha256':hashes,'timeout_seconds':180}
            try:
                run=subprocess.run(command,text=True,capture_output=True,timeout=180)
                words=run.stdout.split()
                if run.returncode or not words or words[-1] not in ('true','false'):
                    raise RuntimeError(run.stderr)
                row.update(status='complete',value=words[-1]=='true')
            except subprocess.TimeoutExpired:
                row.update(status='inconclusive',value=None,reason='180-second limit')
            report['checks'].append(row)
            target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
            print(protocol,equivalence,row['status'],row['value'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--sustained-word-only',action='store_true')
    args=parser.parse_args()
    check_sustained_word() if args.sustained_word_only else main()
