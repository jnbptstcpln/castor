
class NoReturnException(Exception):
    def __init__(self, message=None):
        super().__init__()
        self.message = message


class StopException(Exception):
    def __init__(self, message=None):
        super().__init__()
        self.message = message


class ExitException(Exception):
    def __init__(self, message=None):
        super().__init__()
        self.message = message


class RestartException(Exception):
    def __init__(self, keep_environment=False, message=None):
        super().__init__()
        self.keep_environment = keep_environment
        self.message = message
