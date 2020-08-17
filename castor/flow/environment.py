
import copy

class Environment:

    def __init__(self):
        self.items = {}

    def set(self, key, value):
        self.items[key] = value

    def get(self, key, default=None):
        return self.items.get(key, default)

    def build(self, items=None):
        if type(items) is dict:
            self.items = copy.deepcopy(items)
        else:
            self.items = {}
