
import importlib
import re

from castor.exception import StopException, ExitException
from castor.helper import Doc

class Component:

    def __init__(self, settings):
        self.settings = settings
        self._inputs = None
        self._outputs = None
        self._doc = None

    @property
    def doc(self):
        if self._doc is None:
            # Parse self.func.__doc__ to get information about the inputs and output
            self._doc = Doc(self.func)
        return self._doc

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = []
            for param in self.doc.inputs:
                self._inputs.append(param)
        return self._inputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._outputs = []
            for param in self.doc.outputs:
                self._outputs.append(param)
        return self._outputs

    def func(self, *kwargs):
        """Code that will be executed each time the component is run"""
        pass

    def stop(self):
        """Stop the execution of the component"""
        raise StopException()

    def exit(self):
        """Stop the execution of the flow"""
        raise ExitException()


class ComponentSettings:

    def __init__(self, dict):
        self.dict = dict

    def get(self, key, default=None):
        if key in self.dict.keys():
            return self.dict[key]
        else:
            return default


class ComponentPort:

    def __init__(self, name):
        self.name = name


class Library:

    def __init__(self, core):
        self.core = core

    def get_local(self, id, settings=None):
        module_part = id.split(".")
        component_name = module_part.pop()
        module_id = ".".join(module_part)

        # Try to import the given module
        # We add the needed prefix to get a valid module name
        try:
            module = importlib.import_module("castor.flow.component." + module_id)
        except ModuleNotFoundError:
            raise Exception("Aucun module nommé '" + module_id + "'")

        try:
            return getattr(module, component_name)(ComponentSettings(settings))
        except AttributeError:
            raise Exception("Aucun composant nommé '" + component_name + "' au sein du module '" + module_id + "'")

    def get(self, id, settings=None, fetch_remote=True):
        # Try to get the component locally
        try:
            return self.get_local(id, settings)
        except Exception as e:
            if not fetch_remote:
                raise e
            pass
        # Connect to Pollux to update or install the module

    def version(self, module_id):
        try:
            module = importlib.import_module("castor.flow.component." + module_id)
            return module.__doc__
        except ModuleNotFoundError:
            raise Exception("Aucun module nommé '" + module_id + "'")


    def install(self, module_id):
        pass

    def update(self, module_id):
        pass


