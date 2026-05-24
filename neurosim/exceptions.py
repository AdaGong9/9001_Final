

class NeuroSimError(Exception):
    pass


class InvalidBrainStateError(NeuroSimError):
    pass


class InvalidSignalParameterError(NeuroSimError):
    pass


class InvalidUserInputError(NeuroSimError):
    pass
