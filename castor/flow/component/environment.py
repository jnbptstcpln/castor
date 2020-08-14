"""
    :version 0.1
"""
from ..component import Component


class Get(Component):
    def func(self):
        """
        :setting variable_name:string
        :return value:string
        """
        return self.environment.get(self.settings.get("variable_name"))


class Set(Component):
    def func(self, value):
        """
        :setting variable_name:string
        :param value:string
        """
        self.environment.set(self.settings.get("variable_name"), value)
