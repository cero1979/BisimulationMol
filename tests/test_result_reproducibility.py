"""Keep scientific regression checks strict across time-bounded search runs."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ResultReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "scripts/verify_result_reproducibility.py"
        cls.checker_path = path
        if path.exists():
            spec = importlib.util.spec_from_file_location("result_check", path)
            cls.checker = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.checker)

    def compare(self, name, left, right):
        self.assertTrue(self.checker_path.exists(), "Missing resource-aware result verifier")
        return self.checker.results_equal(name, json.dumps(left).encode(),
                                          json.dumps(right).encode())

    def test_time_limited_progress_does_not_change_scientific_equivalence(self):
        for suffix in ("sustained_trace_equivalence", "withdrawal_trace_equivalence",
                       "sustained_comparison", "withdrawal_comparison", "trace_equivalence"):
            name = "results/death_receptor_" + suffix + ".json"
            original = json.loads((ROOT / name).read_text())
            changed = copy.deepcopy(original)
            if suffix.endswith("comparison"):
                records = [changed["trace_analysis"]]
            elif suffix == "trace_equivalence":
                records = [changed["sustained"], changed["withdrawal"]]
            else:
                records = [changed]
            for record in records:
                record["subset_product_states"] = 1
                record["stored_subset_bytes"] = 8
            self.assertTrue(self.compare(name, original, changed), name)

    def test_verdict_witness_protocol_and_unfinished_status_stay_strict(self):
        name = "results/death_receptor_sustained_trace_equivalence.json"
        original = json.loads((ROOT / name).read_text())
        changes = {"exact_trace_equal": True, "left_only_trace": [],
                   "known_word_prefix_counts": [], "max_seconds": 1,
                   "status": "complete", "exploration_complete": True,
                   "right_trace_included_in_left": True}
        for key, value in changes.items():
            changed = dict(original, **{key: value})
            self.assertFalse(self.compare(name, original, changed), key)

    def test_graph_size_is_not_a_resource_counter(self):
        name = "results/death_receptor_sustained_comparison.json"
        original = json.loads((ROOT / name).read_text())
        changed = copy.deepcopy(original)
        changed["graphs"]["DR-FB+"]["states"] += 1
        self.assertFalse(self.compare(name, original, changed))

    def test_unlisted_files_keep_byte_comparison(self):
        self.assertFalse(self.compare("results/other.json",
                                      {"subset_product_states": 2},
                                      {"subset_product_states": 1}))

    def test_missing_or_invalid_counters_are_not_silently_ignored(self):
        name = "results/death_receptor_sustained_trace_equivalence.json"
        original = json.loads((ROOT / name).read_text())
        for value in (None, -1, "8", True):
            changed = dict(original, stored_subset_bytes=value)
            with self.assertRaises(ValueError):
                self.compare(name, original, changed)
        changed = dict(original)
        del changed["stored_subset_bytes"]
        with self.assertRaises(ValueError):
            self.compare(name, original, changed)


if __name__ == "__main__":
    unittest.main()
