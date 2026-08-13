"""Regression tests for the formal properties stated in the JMCS manuscript."""

from __future__ import annotations

import random
import unittest

from src import concurrent_biomodels as cbm
from src import method_benchmark as mb
from src import pn_gdda


class FormalPropertyTests(unittest.TestCase):
    def test_strong_bisimilarity_implies_weak_and_mutual_simulation(self) -> None:
        left = mb.linear_workflow(4)
        right = mb.clone_lts(left, "copy")

        self.assertTrue(cbm.strong_bisimilar(left, right))
        self.assertTrue(cbm.weak_bisimilar(left, right))
        self.assertTrue(cbm.weak_simulates(left, right))
        self.assertTrue(cbm.weak_simulates(right, left))

    def test_controlled_silent_refinement_is_weak_but_not_strong(self) -> None:
        base = mb.linear_workflow(4)
        refined = cbm.refine_with_tau(base, random.Random(11), n_ins=1)

        self.assertFalse(cbm.strong_bisimilar(base, refined))
        self.assertTrue(cbm.weak_bisimilar(base, refined))

    def test_equal_exact_traces_do_not_hide_branching_direction(self) -> None:
        late_choice, early_choice = mb.branching_time_trap()
        alphabet = late_choice.observables | early_choice.observables

        # Both acyclic systems have maximum observable trace length two.
        self.assertEqual(
            cbm.observable_language(late_choice, 3, alphabet),
            cbm.observable_language(early_choice, 3, alphabet),
        )
        self.assertFalse(cbm.weak_bisimilar(late_choice, early_choice))
        self.assertTrue(cbm.weak_simulates(early_choice, late_choice))
        self.assertFalse(cbm.weak_simulates(late_choice, early_choice))

    def test_mutual_simulation_does_not_imply_bisimilarity(self) -> None:
        left = cbm.LTS(
            "a-bc-plus-ab",
            ["l0", "lbc", "lb", "lbt", "lct", "lbt2"],
            0,
            [
                (0, "a", 1),
                (0, "a", 2),
                (1, "b", 3),
                (1, "c", 4),
                (2, "b", 5),
            ],
        )
        right = cbm.LTS(
            "a-bc",
            ["r0", "rbc", "rbt", "rct"],
            0,
            [(0, "a", 1), (1, "b", 2), (1, "c", 3)],
        )

        self.assertTrue(cbm.weak_simulates(left, right))
        self.assertTrue(cbm.weak_simulates(right, left))
        self.assertFalse(cbm.weak_bisimilar(left, right))
        self.assertEqual(mb.classify_pair(left, right)["formal_class"], "mutual simulation")

    def test_truncated_trace_match_does_not_claim_exact_trace_equality(self) -> None:
        left = mb.linear_workflow(4)
        right = mb.add_observable_branch(left, source=3, label="late_extra")
        alphabet = left.observables | right.observables

        self.assertEqual(
            cbm.observable_language(left, 2, alphabet),
            cbm.observable_language(right, 2, alphabet),
        )
        self.assertNotEqual(
            cbm.observable_language(left, 6, alphabet),
            cbm.observable_language(right, 6, alphabet),
        )

    def test_tau_closure_matches_zero_or_more_internal_steps(self) -> None:
        direct = cbm.LTS("direct", ["d0", "d1"], 0, [(0, "a", 1)])
        refined = cbm.LTS(
            "refined",
            ["r0", "r1", "r2", "r3", "r4"],
            0,
            [
                (0, cbm.TAU, 1),
                (1, cbm.TAU, 2),
                (2, "a", 3),
                (3, cbm.TAU, 4),
            ],
        )

        self.assertEqual(refined.tau_closure(0), frozenset({0, 1, 2}))
        self.assertEqual(refined.weak_step(0, "a"), frozenset({3, 4}))
        self.assertFalse(cbm.strong_bisimilar(direct, refined))
        self.assertTrue(cbm.weak_bisimilar(direct, refined))

    def test_simulation_orientation_is_reference_contained_in_candidate(self) -> None:
        reference = mb.linear_workflow(3)
        candidate = mb.add_observable_branch(reference, source=1, label="extra")

        self.assertTrue(cbm.weak_simulates(reference, candidate))
        self.assertFalse(cbm.weak_simulates(candidate, reference))
        self.assertEqual(
            mb.classify_pair(reference, candidate)["formal_class"],
            "reference simulated by candidate",
        )

    def test_label_renaming_preserves_unlabelled_topology_not_behaviour(self) -> None:
        left = cbm.LTS("left", ["s0", "s1"], 0, [(0, "a", 1)])
        right = cbm.LTS("right", ["s0", "s1"], 0, [(0, "b", 1)])

        self.assertEqual(
            [(source, target) for source, _label, target in left.edges],
            [(source, target) for source, _label, target in right.edges],
        )
        self.assertEqual(
            pn_gdda.pn_gdda_similarity(
                pn_gdda.state_machine_petri(left),
                pn_gdda.state_machine_petri(right),
                holmes_compatible=True,
            ),
            1.0,
        )
        self.assertFalse(cbm.weak_simulates(left, right))
        self.assertFalse(cbm.weak_simulates(right, left))
        self.assertFalse(cbm.weak_bisimilar(left, right))

    def test_classifier_returns_one_exclusive_priority_class(self) -> None:
        allowed = {
            "strong equivalence",
            "weak equivalence",
            "mutual simulation",
            "reference simulated by candidate",
            "candidate simulated by reference",
            "not comparable",
        }
        rows = mb.validation_benchmark()

        self.assertTrue(all(row["formal_class"] in allowed for row in rows))
        self.assertEqual(rows[0]["formal_class"], "strong equivalence")
        self.assertEqual(rows[1]["formal_class"], "weak equivalence")

    def test_benchmark_table_is_deterministic(self) -> None:
        first = mb.validation_benchmark()
        second = mb.validation_benchmark()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 6)
        self.assertTrue(all(row["formal_match"] for row in first))


if __name__ == "__main__":
    unittest.main()
