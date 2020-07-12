"""
    :version 0.1
"""
from ..component import Component


class Addition(Component):
    def func(self, a, b):
        """
        :param a:float
        :param b:float
        :return result:float
        """
        return a+b


class Multiplication(Component):
    def func(self, a, b):
        """
        :param a:float
        :param b:float
        :return result:float
        """
        return a*b
