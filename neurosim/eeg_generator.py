
import numpy as np
from typing import Tuple

from exceptions import InvalidBrainStateError, InvalidSignalParameterError


# Frequency-band definitions for each brain state (Hz)
BRAIN_STATES = {
    "delta": {"band": (0.5, 4),  "label": "Deep Sleep"},
    "theta": {"band": (4, 8),    "label": "Drowsy / Meditative"},
    "alpha": {"band": (8, 13),   "label": "Relaxed"},
    "beta":  {"band": (13, 30),  "label": "Focused"},
    "gamma": {"band": (30, 50),  "label": "High Cognition"},
}


class EEGGenerator:

    def __init__(self, sampling_rate: int = 250, duration: float = 4.0,
                 n_channels: int = 4):
        if sampling_rate <= 0 or duration <= 0 or n_channels <= 0:
            raise InvalidSignalParameterError(
                "sampling_rate, duration, and n_channels must all be positive."
            )
        self.fs = sampling_rate
        self.duration = duration
        self.n_channels = n_channels
        self.n_samples = int(sampling_rate * duration)
        # Shared time axis for all channels
        self.t = np.linspace(0, duration, self.n_samples, endpoint=False)

    def generate(self, state: str, noise_level: float = 0.3) -> np.ndarray:
        if state not in BRAIN_STATES:
            raise InvalidBrainStateError(
                f"Unknown brain state '{state}'. "
                f"Valid options: {list(BRAIN_STATES.keys())}"
            )

        low, high = BRAIN_STATES[state]["band"]

        # 2D array: (channels x samples)  -- Advanced Topic: NumPy
        signal = np.zeros((self.n_channels, self.n_samples))

        for ch in range(self.n_channels):
            # Sum 5 random sinusoids inside the target band
            for _ in range(5):
                freq = np.random.uniform(low, high)
                phase = np.random.uniform(0, 2 * np.pi)
                amplitude = np.random.uniform(0.5, 1.5)
                signal[ch] += amplitude * np.sin(2 * np.pi * freq * self.t + phase)

            # Add a small amount of pink-ish background activity (low-freq drift)
            drift_freq = np.random.uniform(0.1, 0.5)
            signal[ch] += 0.3 * np.sin(2 * np.pi * drift_freq * self.t)

            # Add Gaussian noise
            signal[ch] += noise_level * np.random.randn(self.n_samples)

        return signal

    def compute_psd(self, signal_1d: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        fft_vals = np.fft.rfft(signal_1d)
        freqs = np.fft.rfftfreq(len(signal_1d), d=1.0 / self.fs)
        power = np.abs(fft_vals) ** 2
        return freqs, power

    def band_power(self, signal_1d: np.ndarray, state: str) -> float:
        if state not in BRAIN_STATES:
            raise InvalidBrainStateError(f"Unknown brain state '{state}'.")
        low, high = BRAIN_STATES[state]["band"]
        freqs, power = self.compute_psd(signal_1d)
        mask = (freqs >= low) & (freqs <= high)
        return float(power[mask].sum())


def classify_by_band_power(signal_1d: np.ndarray, generator: EEGGenerator) -> str:
    powers = {
        state: generator.band_power(signal_1d, state)
        for state in BRAIN_STATES
    }
    return max(powers, key=powers.get)
