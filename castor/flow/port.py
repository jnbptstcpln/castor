
from castor.datatype import Library as DatatypeLibrary
from collections import deque
from castor.helper import Setting


class Port:

    def __init__(self, name, type, settings=None):
        self.name = name
        self.type = type
        self._type = DatatypeLibrary.get(self.type)
        self.settings = PortSettings(settings)
        self.value = None
        self.buffer = deque([])

    def cast(self, value):
        if self._type:
            try:
                return self._type(value)
            except BaseException as err:
                raise Exception("Une erreur est survenu lors du casting : {}".format(err))
        return value

    def set(self, value):
        self.value = self.cast(value)

    def push(self, value):
        self.buffer.append(value)

    def clear(self):
        self.value = None

    @property
    def isset(self):
        # Check if the current value is None
        if self.value is None:
            if len(self.buffer) > 0:
                self.set(self.buffer.popleft())
                return True
            return False
        return True

    @property
    def is_buffer_full(self):
        return len(self.buffer) >= self.settings.buffer_size


class PortSettings(Setting):
    @property
    def buffer_size(self):
        return self.get("buffer_size", 1)
