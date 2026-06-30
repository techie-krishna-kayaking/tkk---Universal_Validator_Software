class ExecutionEngineError(Exception):
    pass


class EngineUnavailableError(ExecutionEngineError):
    pass


class EngineExecutionError(ExecutionEngineError):
    pass


class EngineSelectionError(ExecutionEngineError):
    pass
