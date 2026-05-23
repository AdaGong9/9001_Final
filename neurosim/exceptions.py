"""
exceptions.py — Custom exception classes for NeuroSim.

This module is imported by other modules — do NOT run it directly.
Run `python main.py` instead.

Advanced topic demonstrated in this file:
    - More Flow Control (raise, custom exception hierarchy)
"""


class NeuroSimError(Exception):
    """Base exception for all NeuroSim errors."""
    pass


class InvalidBrainStateError(NeuroSimError):
    """Raised when an unknown brain state is requested."""
    pass


class InvalidSignalParameterError(NeuroSimError):
    """Raised when EEG generation parameters are invalid."""
    pass


class InvalidUserInputError(NeuroSimError):
    """Raised when the user's input cannot be interpreted."""
    pass
