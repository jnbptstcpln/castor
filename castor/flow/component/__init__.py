

import importlib
import hashlib
import codecs
import os

from castor.exception import StopException, ExitException, RestartException
from castor.helper import Doc


class Component:

    def __init__(self, settings):
        self.settings = settings
        self.node = None
        self._inputs = None
        self._outputs = None
        self._doc = None

    @property
    def flow(self):
        return self.node.flow

    @property
    def environment(self):
        return self.node.flow.environment

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

    def restart(self, keep_environment=False, message=""):
        """Restart execution of the flow"""
        raise RestartException(keep_environment, message)


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
        self._modules = {}
        self.modules = {}

    def reload(self):
        self.modules = {}

    def get_module(self, module_id, use_remote=True):
        """
        Return the corresponding module stored if self.modules or load it if it wasn't already
        if use_remote=True, the library fetch update from Pollux or install the module locally if it wasn't already
        """
        if not module_id in self.modules.keys():
            path = self.id_to_path(module_id)
            if os.path.exists(path):
                try:
                    # Update the module
                    if use_remote:
                        self.update(module_id)

                    # Check if the module was already loaded
                    if module_id in self._modules.keys():
                        self._modules[module_id] = importlib.reload(self._modules[module_id])
                    else:
                        self._modules[module_id] = importlib.import_module("castor.flow.component." + module_id)

                    self.modules[module_id] = self._modules[module_id]

                except ModuleNotFoundError as e:
                    message = "Erreur lors de l'importation du module nommé '{}' : \"{}\"".format(module_id, e)
                    self.core.log(message)
                    raise Exception(message)
                except BaseException as e:
                    message = "Une erreur est survenu lors du chargement du module '{}' : \"{}\"".format(module_id, e)
                    self.core.log(message)
                    raise Exception(message)

            elif use_remote:
                # Search the module on Pollux
                modules = self.remote_search(module_id)
                if len(modules) == 0:
                    message = "Aucun module nommé '{}' n'a pu être trouvé sur Pollux".format(module_id)
                    self.core.log(message)
                    raise Exception(message)
                self.install(module_id)
                return self.get_module(module_id, use_remote)

            else:
                message = "Aucun module nommé '{}' n'a pu être trouvé en local".format(module_id)
                self.core.log(message)
                raise Exception(message)

        return self.modules[module_id]

    def get_component(self, id, settings=None, use_remote=True):
        """
        Return an instance of the corresponding Component
        """

        # Break the component's id in two part : module's id and component's name
        module_part = id.split(".")
        component_name = module_part.pop()
        module_id = ".".join(module_part)

        # Get the module
        module = self.get_module(module_id, use_remote)

        try:
            return getattr(module, component_name)(ComponentSettings(settings))
        except AttributeError:
            raise Exception("Aucun composant nommé '" + component_name + "' au sein du module '" + module_id + "'")

    def get(self, id, settings=None, use_remote=True):
        """
        Return an instance of the corresponding Component
        """
        return self.get_component(id, settings, use_remote)

    def hash(self, module_id):
        """
        Return the hash of the file corresponding to the given module
        """
        sha1sum = hashlib.sha1()
        with open(self.id_to_path(module_id), 'rb') as source:
            block = source.read(2 ** 16)
            while len(block) != 0:
                sha1sum.update(block)
                block = source.read(2 ** 16)
        return sha1sum.hexdigest()

    def id_to_path(self, module_id):
        """
        Concert the given module_id to the correspond path to the file
        :param module_id:
        :return:
        """
        libraryPath = os.path.dirname(__file__)
        parts = module_id.split('.')
        fileName = "{}.py".format(parts.pop())
        modulePath = os.path.join(libraryPath, *parts, fileName)
        return modulePath

    def remote_search(self, module_id):
        """
        Perform a search on Pollux for the given module_id
        :param module_id:
        :return:
        """
        try:
            rep = self.core.pollux.api.get("/api/modules/search", {"module_id": module_id})
            if rep.get("success", False):
                return rep.get("payload", {})
        except Exception as e:
            self.core.log(e)
            raise Exception(e)

    def install(self, module_id):
        """
        Fetch the content of the corresponding module and store it as a Python file inside
        :param module_id:
        :return:
        """
        try:
            rep = self.core.pollux.api.get("/api/modules/i/{}/download".format(module_id))
            if rep.get("success", False):
                payload = rep.get("payload", {})
                path = self.id_to_path(module_id)
                # Create parent directories
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with codecs.open(path, 'w', 'utf-8') as f:
                    f.write(payload.get('content', ""))
        except Exception as e:
            message = "Impossible d'installer le module '{}' : {}".format(module_id, e)
            self.core.log(message)
            raise Exception(message)

    def update(self, module_id):
        """

        :param module_id:
        :return:
        """
        rep = self.core.pollux.api.get("/api/modules/i/{}/hash".format(module_id))
        if rep.get("success", False):
            payload = rep.get("payload", {})
            remote_hash = payload.get("hash", None)
            if remote_hash != self.hash(module_id):
                self.install(module_id)
        else:
            message = "Impossible de mettre à jour le module '{}'".format(module_id)
            self.core.log(message)



