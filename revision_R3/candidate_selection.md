# Candidate selection, R3

## Candidate 1: selected at Pattern B, not Pattern A

The pinned Calzone 2010 model and its literature-described CASP3-to-CASP8 edge-deletion variant share exactly the same reachable stable-fate set under sustained TNF: survival, apoptosis, necrosis. The fixed interface is NFkB/CASP3/MPT up/down, with a common withdraw_TNF intervention. No labels were changed after results.

An automatically selected, jointly reachable CASP3-positive state follows eight raw updates and visible history CASP3_up. From this state, the sustained continuations are strongly and weakly bisimilar and have exact language {epsilon}. Permitting withdrawal produces 12-state and 34-state continuations: FB+ is simulated by FB-, not conversely. The latter can execute withdraw_TNF, CASP3_down; the former cannot. After immediate withdrawal, terminal fate is uniquely apoptosis for FB+ and naive for FB-. The continuation graphs are acyclic; marker persistence is checked separately from terminal reachability.

The complete visible prefix CASP3_up is compatible with 78 hidden states in each model. It does not uniquely identify the selected state. Aggregated terminal futures after withdrawal are {apoptosis, naive, necrosis} for FB+ and {naive, necrosis} for FB-. The withdrawal-aware global languages are unequal in both inclusion directions, supported by exact counterexample traces. Thus this is NOT an example where global traces remain equal while branching alone separates models.

The subsequent expanded search refuted global sustained trace equality with a 12-action word possible only in FB+. Independent sparse reachability and mCRL2 confirm it. Thus FB- cannot weakly simulate FB+ and weak bisimulation fails; the reverse inclusion remains undecided. The supported contribution is still an intervention/commitment comparison of endpoint-matched models, not separation attributable exclusively to branching.

## Candidate 2: subsequently tested in a separate feasibility probe

The initial R3 plan did not execute the conditional fallback because Calzone met Pattern B. A later user-authorized probe compared the public 2006/2016 cell-cycle models under fixed cyclin and shared-regulator interfaces, with sustained input and input withdrawal. All four comparisons had unequal traces and failed weak bisimulation, so none meets Pattern A. The probe is not added to the paper as branching-only biological evidence. A stronger equal-global-trace/different-branching biological demonstration remains open.

## Novelty and evidence

Calzone et al. already studied both the feedback and ligand withdrawal. The contribution here is a fixed-interface relational reconstruction, explicit shared-state/history witness, scope-controlled fate analysis, and separation of specified mechanisms from computed results. It is not a new biological mechanism or wet-lab validation. GIM becomes a secondary illustration restricted to its three declared interfaces.
