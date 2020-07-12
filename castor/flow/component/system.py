"""
    :version 0.1
"""
from castor.flow.component import Component


class Print(Component):
    def func(self, value):
        """
        :param value:string
        :return value:string
        """
        print(value)
        return value


class Exit(Component):
    def func(self, value):
        """
        :param value:string
        """
        self.exit()
