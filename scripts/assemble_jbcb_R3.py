"""Assemble R3, preserving the authoritative R2 and accepted mathematics."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.assemble_jbcb_R2 import bibliography_for
OUT=ROOT/'revision_R3'
TITLE='Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models'


def mathematical_blocks(text):
    pattern=r'\\begin\{(definition|proposition|example|algorithm|theorem|proof)\}.*?\\end\{\1\}'
    return [m.group(0) for m in re.finditer(pattern,text,re.S)]


def numeric_macros():
    w=json.loads((ROOT/'results/death_receptor_branching_witness.json').read_text())
    s=json.loads((ROOT/'results/death_receptor_execution_summary.json').read_text())
    t=json.loads((ROOT/'results/death_receptor_sustained_trace_equivalence.json').read_text())
    values={}
    for side,model in [('Plus','DR-FB+'),('Minus','DR-FB-')]:
        for mode,protocol in [('Base','sustained'),('Control','withdrawal')]:
            for quantity in ('states','edges'):
                values['DR'+mode+side+quantity.title()]=s['models'][model][protocol][quantity]
    for side,g in zip(('Plus','Minus'),w['local_graphs']):
        values['DRLocal'+side+'States']=g['states']
        values['DRLocal'+side+'Edges']=len(g['edges'])
    with (ROOT/'results/death_receptor_commitment_scan.csv').open() as handle:
        rows=list(csv.DictReader(handle))
    first=next(r for r in rows if r['model']=='DR-FB+' and int(r['states_with_persistent_CASP3']))
    values.update(DRDepth=w['common_raw_history']['raw_depth'],
                  DRLocalBaseStates=w['conditioned_sustained']['graphs'][0]['states'],
                  DRLocalBaseEdges=w['conditioned_sustained']['graphs'][0]['edges'],
                  DRHistoryStates=w['history_aggregated_futures']['DR-FB+']['compatible_states_before_withdrawal'],
                  DRFirstCommitted=int(first['states_with_persistent_CASP3']),
                  DRDepthStates=int(first['reachable_states_before_withdrawal']),
                  DRBaseSubsetPairs=t['subset_product_states'],DRBaseSubsetBytes=t['stored_subset_bytes'])
    return '\n'.join('\\newcommand{\\'+key+'}{'+format(value,',').replace(',','{,}')+'}'
                     for key,value in sorted(values.items()))+'\n'


def section(name):
    return (OUT/'sections'/f'{name}.tex').read_text().strip()+'\n\n'


def assemble():
    source=ROOT/'revision_R2/main_jbcb_R2.tex'
    original=source.read_text()
    assert hashlib.sha256(source.read_bytes()).hexdigest()=='e54695a277c691b88a0e95bb5de65e39bc7441cb2c253d9b17d2f20ed839059f'
    preserved=OUT/'original_R2'
    preserved.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,preserved/source.name)
    macros=numeric_macros()
    def between(start,end):
        return original[original.index(start):original.index(end)]
    prefix=original[:original.index('\\begin{abstract}')]
    prefix=prefix.replace('Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models',TITLE)
    prefix=prefix.replace('Resolution-dependent correspondence in DNA-damage models','Resolution-dependent behavioral correspondence')
    prefix=prefix.replace('\\begin{document}',macros+'\n\\begin{document}')
    biology=between('\\section{Biological comparison problem','\\section{Computational comparison method}')
    head,rest=biology.split('\\subsection',1)
    rest=('\\subsection'+rest).replace('Biological question and observational-interface principles','GIM as an interface-sensitivity problem')
    biology=head+section('death_models')+rest.replace('The central question is whether','The secondary question is whether')
    method=between('\\section{Computational comparison method}','\\section{Main result:')
    method+='The accepted early/late-choice example supplies the conceptual target: equal histories need not preserve the same future choices. The biological analysis below tests a related intervention question without assuming equal global trace languages.\n\n'
    gim=between('\\section{Main result:','\\section{Supporting curated comparisons}')
    gim=gim.replace('Main result: a resolution boundary in GIM','GIM illustration: interface-conditioned behavioral correspondence')
    gim=gim.replace('The observed boundary is therefore','The first loss of correspondence is therefore')
    supporting=between('\\section{Supporting curated comparisons}','\\section{Supporting formal and implementation checks}')
    supporting=supporting.replace('Supporting curated comparisons','Supporting and exploratory comparisons',1)
    supporting=supporting.replace('\\section{Exploratory confrontation with HPN-DREAM data}',
                                  '\\subsection{Exploratory confrontation with HPN-DREAM data}')
    validation=between('\\section{Supporting formal and implementation checks}','\\section{Discussion}')
    validation=validation.replace('and scaling details; the principal GIM evidence remains in Section~4.',
                                  'and scaling details; the main death-receptor evidence is in Section~4 and GIM in Section~5.')
    validation+=r'''
The new death-receptor checks distinguish global from conditioned comparisons.
Compact Boolean execution is checked against the tuple-based executor;
the selected full 28-node continuations reproduce the quotient's weak results.
The exact conditioned sustained languages agree, while withdrawal gives one-way
simulation, confirmed by a raw-edge game certificate covering every defender
reply. mCRL2 independently confirms all six strong/weak/trace equivalence
decisions across the two conditioned protocols. Global withdrawal simulations
are refuted by exact trace counterexamples in both directions. An
independent tuple/product search using all 28 original rule callbacks
confirms acceptance in one variant and exhaustive rejection in the other for
each withdrawal counterexample, without compact storage or sink reduction.
Global sustained trace equality is also refuted: a 12-action word is possible
only in DR-FB+, as independently checked by sparse reachability and mCRL2.
A reconstructed 53-update accepting path satisfies the original full-model
rules. The reverse sustained inclusion remains undecided. The expanded
subset search still reaches its storage cap, but the finite witness suffices
to disprove equality; this is not an inference from resource exhaustion.
Supplementary Validation S5 gives the reduction argument, full graph sizes,
execution limits and event-depth scan. These limits are not counted as
failed equivalences or as successful biological validations.

'''
    appendices=between('\\appendix','\\section*{Data and code availability}')
    declarations=between('\\section*{Data and code availability}','\\begin{thebibliography}')
    declarations=declarations.replace('The second-revision source and audits are in \\texttt{revision\\_R2/}.',
                                      'The accompanying R3 reproducibility archive supplies the third-revision sources, executed notebook, exact continuation outputs, and execution protocol; these additions are not yet a separately published remote release.')
    bib=original[original.index('\\begin{thebibliography}'):original.index('\\end{thebibliography}')+len('\\end{thebibliography}')]
    calzone=r'''
\bibitem{Calzone2010}
Calzone L, Tournier L, Fourquet S, Thieffry D, Zhivotovsky B, Barillot E,
Zinovyev A, Mathematical modelling of cell-fate decision in response to death
receptor engagement, \emph{PLoS Computational Biology} \textbf{6}(3):e1000702, 2010.
\newblock \doi{10.1371/journal.pcbi.1000702}.

'''
    bib=bib.replace('\\end{thebibliography}',calzone+'\\end{thebibliography}')
    body=(prefix+'\\begin{abstract}\n'+section('abstract')+'\\end{abstract}\n\n'
          +'\\keywords{Cell-fate commitment; death-receptor signaling; qualitative models; signal withdrawal; weak bisimulation.}\n\n'
          +section('introduction')+biology+method+section('death_results')+gim+supporting+validation
          +section('discussion')+appendices+declarations)
    body=body.replace('R2_Fig','R3_Fig')
    main=body+bibliography_for(body,bib)+'\n\\end{document}\n'
    assert mathematical_blocks(main)==mathematical_blocks(original)
    (OUT/'main_jbcb_R3.tex').write_text(main)
    for name in ('ws-jbcb.cls','R2_Fig2.pdf','R2_Fig3.pdf','R2_Fig4.pdf','R2_SFig1.pdf','R2_SFig2.pdf'):
        shutil.copy2(ROOT/'revision_R2'/name,OUT/name.replace('R2_','R3_'))
    supplement=(ROOT/'revision_R2/Supplementary_Validation_R2.tex').read_text().replace('R2_SFig','R3_SFig')
    supplement=supplement.replace('Second major revision','Third major revision').replace('second major revision','third major revision')
    supplement=supplement.replace('JBCB-1505 R2', 'JBCB-1505 R3')
    supplement=supplement.replace('Supplementary Validation: Resolution-dependent correspondence in DNA-damage models',
                                  'Supplementary Validation: '+TITLE)
    supplement=supplement.replace('Supplementary Validation: Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models',
                                  'Supplementary Validation: '+TITLE)
    supplement=supplement.replace('It is not independent\nbiological validation of the curated GIM models.',
                                  'It includes the death-receptor execution audit in Section~S5. It is not independent wet-lab validation of either biological case.')
    supplement=supplement.replace('\\begin{document}',macros+'\n\\begin{document}')
    supplement=supplement.replace('\\begin{thebibliography}',section('supplement')+'\\begin{thebibliography}',1)
    (OUT/'Supplementary_Validation_R3.tex').write_text(supplement)
    (OUT/'response_to_reviewer_R3.tex').write_text(section('response').replace('@@NUMBERS@@',macros))
    (OUT/'mathematics_preservation_R3.json').write_text(json.dumps({
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'identical_accepted_environments':len(mathematical_blocks(original)),
        'mathematics_changed':False},indent=2)+'\n')
    print('Assembled R3; accepted mathematical environments preserved:',len(mathematical_blocks(original)))


if __name__=='__main__':
    assemble()
