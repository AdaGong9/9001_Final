"""
test_neurosim.py — Unit tests for NeuroSim.

This file contains 11 unit tests covering the signal generator, rule-based
classifier, and JSON score storage. To run them:

    python -m unittest test_neurosim.py -v

All tests should pass. (Note: main.py is the entry point for the program
itself — this file only runs the test suite.)

Advanced topic demonstrated in this file:
    - Testing (unittest module)
"""

import os
import tempfile
import unittest

import numpy as np

from eeg_generator import (
    EEGGenerator, BRAIN_STATES, classify_by_band_power
)
from exceptions import (
    InvalidBrainStateError, InvalidSignalParameterError
)
import data_manager


class TestEEGGenerator(unittest.TestCase):
    """Tests for the EEG signal generator."""

    def setUp(self):
        self.gen = EEGGenerator(sampling_rate=250, duration=2.0, n_channels=4)

    def test_signal_shape(self):
        signal = self.gen.generate("alpha")
        self.assertEqual(signal.shape, (4, 500))

    def test_signal_is_finite(self):
        signal = self.gen.generate("beta")
        self.assertTrue(np.isfinite(signal).all())

    def test_all_states_supported(self):
        for state in BRAIN_STATES:
            signal = self.gen.generate(state)
            self.assertEqual(signal.shape, (4, 500))

    def test_invalid_state_raises(self):
        with self.assertRaises(InvalidBrainStateError):
            self.gen.generate("not_a_real_state")

    def test_invalid_params_raise(self):
        with self.assertRaises(InvalidSignalParameterError):
            EEGGenerator(sampling_rate=-1)
        with self.assertRaises(InvalidSignalParameterError):
            EEGGenerator(duration=0)

    def test_band_power_in_correct_band(self):
        """A signal generated for 'alpha' should have most of its
        power inside the alpha band (8-13 Hz)."""
        signal = self.gen.generate("alpha", noise_level=0.05)
        powers = {
            state: self.gen.band_power(signal[0], state)
            for state in BRAIN_STATES
        }
        self.assertEqual(max(powers, key=powers.get), "alpha")

    def test_psd_shape(self):
        signal = self.gen.generate("theta")
        freqs, power = self.gen.compute_psd(signal[0])
        self.assertEqual(len(freqs), len(power))
        # rfft output length = n_samples//2 + 1
        self.assertEqual(len(freqs), 500 // 2 + 1)


class TestClassifier(unittest.TestCase):
    """The rule-based classifier should usually identify clean signals."""

    def test_classifier_on_clean_signal(self):
        gen = EEGGenerator(sampling_rate=250, duration=4.0, n_channels=1)
        correct = 0
        total = 0
        for state in BRAIN_STATES:
            for _ in range(3):
                signal = gen.generate(state, noise_level=0.05)
                if classify_by_band_power(signal[0], gen) == state:
                    correct += 1
                total += 1
        # Well above chance (chance = 1/5 = 20%)
        self.assertGreater(correct / total, 0.7)


class TestDataManager(unittest.TestCase):
    """Tests for the JSON-based score storage."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._original_path = data_manager.SCORES_FILE
        data_manager.SCORES_FILE = os.path.join(self.tmpdir.name, "scores.json")

    def tearDown(self):
        data_manager.SCORES_FILE = self._original_path
        self.tmpdir.cleanup()

    def test_empty_load(self):
        self.assertEqual(data_manager.load_scores(), [])

    def test_save_and_load_roundtrip(self):
        data_manager.save_score("Ada", 4, 5, ai_score=3)
        scores = data_manager.load_scores()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["player"], "Ada")
        self.assertEqual(scores[0]["score"], 4)
        self.assertEqual(scores[0]["accuracy"], 0.8)

    def test_leaderboard_sorted(self):
        data_manager.save_score("A", 2, 5)
        data_manager.save_score("B", 5, 5)
        data_manager.save_score("C", 3, 5)
        board = data_manager.get_leaderboard(3)
        self.assertEqual([r["player"] for r in board], ["B", "C", "A"])


if __name__ == "__main__":
    unittest.main()
