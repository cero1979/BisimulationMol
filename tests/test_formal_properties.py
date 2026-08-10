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
