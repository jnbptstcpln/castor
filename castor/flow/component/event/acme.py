"""
    :version 0.1
"""
from castor.flow.component import Component


class HelloWorld(Component):
    def func(self):
        """
        :return value:string
        """
        return "Hello World"
