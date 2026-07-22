"""Exhaustive validation of the independent weak-simulation game oracle."""

from __future__ import annotations

import unittest

from src import simulation_oracle as oracle


class SimulationOracleTests(unittest.TestCase):
    def test_all_one_and_two_state_lts_pairs_agree(self) -> None:
        result = oracle.exhaustive_simulation_validation(max_states=2)
        self.assertEqual(result["number_of_lts"], 260)
        self.assertEqual(result["ordered_lts_pairs"], 67_600)
        self.assertEqual(result["disagreements"], 0)
        self.assertTrue(result["complete_agreement"])


if __name__ == "__main__":
    unittest.main()
