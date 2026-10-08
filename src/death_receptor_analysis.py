"""Pinned Calzone 2010 full-model variants for the fixed-interface Journal study."""

from dataclasses import asdict, replace
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET

from .public_validation import PublicModelSource, load_ginml


SOURCE = PublicModelSource(
    key='death_receptor_calzone2010',
    title='Cell-Fate Decision in Response to Death Receptor Engagement',
    format='GINML', filename='Calzone__Cell_Fate.zginml',
    url='https://ginsim.github.io/models/2010-mammal-cell-fate/Calzone__Cell_Fate.zginml',
    sha256='1cdbf6a3fb00fcf7ce9d63cb753a9bf4a58ea1e16486abb6a49a2016634a6993',
    publication_doi='10.1371/journal.pcbi.1000702',
    repository_page='https://ginsim.github.io/models/2010-mammal-cell-fate/',
    initial_condition='TNF=FADD=ATP=cIAP=1; all other nodes=0',
)
OBSERVABLES = ('NFkB', 'CASP3', 'MPT')
SUSTAINED_COUNTEREXAMPLE = (
    'MPT_up', 'CASP3_up', 'CASP3_down', 'NFkB_up', 'NFkB_down', 'MPT_down',
    'CASP3_up', 'CASP3_down', 'CASP3_up', 'CASP3_down', 'CASP3_up', 'CASP3_down',
)


def validate_download(data):
    actual = hashlib.sha256(data).hexdigest()
    if actual != SOURCE.sha256:
        raise ValueError(f'SHA-256 mismatch for Calzone model: {actual}')


def load_variants():
    validate_download(SOURCE.path.read_bytes())
    original = load_ginml(SOURCE)
    initial = tuple(int(v in {'TNF', 'FADD', 'ATP', 'cIAP'}) for v in original.variables)
    plus = replace(original, name='DR-FB+', initial=initial)
    original_rule = plus.rules['CASP8']

    def without_feedback(values):
        return original_rule(dict(values, CASP3=0))

    minus = replace(plus, name='DR-FB-', rules=dict(plus.rules, CASP8=without_feedback))
    return plus, minus


def configuration():
    plus, _ = load_variants()
    return {
        'source': asdict(SOURCE),
        'variants': {'DR-FB+': 'original published CASP8 rule',
                     'DR-FB-': 'only CASP8 rule reads CASP3 as 0; CASP3 remains dynamic'},
        'initial_state': dict(zip(plus.variables, plus.initial)),
        'update_semantics': 'unitary asynchronous; inputs fixed except controlled TNF withdrawal',
        'interface': {
            'observable_components': list(OBSERVABLES),
            'hidden_components': [v for v in plus.variables if v not in OBSERVABLES],
            'node_mapping': {v: v for v in plus.variables},
            'observable_actions': [f'{v}_{d}' for v in OBSERVABLES for d in ('up', 'down')]
                                 + ['withdraw_TNF'],
            'silent_action': 'tau',
            'justification': 'Published fate readouts: NFkB survival, CASP3 apoptosis, MPT necrosis. '
                             'ATP depletion is additionally required for terminal necrosis classification.',
        },
        'intervention': 'withdraw_TNF is enabled at every state with TNF=1; changes only TNF to 0, '
                        'irreversibly; identical availability in both variants',
        'fates': {'survival': 'NFkB=1, CASP3=MPT=0',
                  'apoptosis': 'CASP3=1, NFkB=MPT=0',
                  'necrosis': 'MPT=1, ATP=0, CASP3=NFkB=0',
                  'naive': 'NFkB=CASP3=MPT=0, ATP=1',
                  'other': 'mixed or varying terminal signature'},
        'literature_rationale': 'Calzone 2010 Discussion and Figs S2/S3 document edge removal and '
                                'transient vs sustained ligand; this is not a new biological discovery.',
        'literature_scope': 'Full 28-node public model; not an exact reproduction of reduced-model '
                            'Monte Carlo probabilities or durations. No physical-time calibration.',
        'limits': {'reachable_states': 200000, 'subset_product_states': 10000,
                   'direct_game_pairs': 1000000, 'withdrawal_event_depth': 40},
    }


def config_hash(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def regulatory_dependencies():
    with zipfile.ZipFile(SOURCE.path) as archive:
        root = ET.fromstring(archive.read('GINsim-data/regulatoryGraph.ginml'))
    result = {node.get('id'):[] for node in root.iter('node')}
    for edge in root.iter('edge'):
        result[edge.get('to')].append(edge.get('from'))
    return {v:tuple(sorted(set(regs))) for v,regs in result.items()}
