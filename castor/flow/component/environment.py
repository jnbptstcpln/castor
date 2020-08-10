"""
    :version 0.1
"""
from ..component import Component


class Get(Component):
    def func(self):
        """
        :return value:string
        """
        return self.environment.get(self.settings.get("name"))


class Set(Component):
    def func(self, value):
        """
        :param value:string
        :return value:string
        """
        self.environment.set(self.settings.get("name"), value)
        return value
