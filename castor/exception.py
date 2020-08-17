
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
