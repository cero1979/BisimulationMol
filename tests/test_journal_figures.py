"""Smoke checks for the retained diagnostic artwork path."""

from pathlib import Path
import tempfile
import unittest

import make_figures
from src import concurrent_biomodels as cbm


class JournalFiguresTests(unittest.TestCase):
    def test_reachability_figure_renders_with_observable_and_silent_edges(self):
        lts = cbm.LTS("drawing", ["0", "1", "2"], 0,
                      [(0, "a", 1), (1, "tau", 2)])
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "reachability.png"
            make_figures.draw_lts(lts, str(target), "Reachability")
            self.assertTrue(target.is_file())
            self.assertTrue(target.with_suffix(".pdf").is_file())


if __name__ == "__main__":
    unittest.main()
