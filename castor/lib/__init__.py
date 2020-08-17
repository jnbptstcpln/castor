import importlib
import hashlib
import codecs
import os


class Library:

    def __init__(self, core):
        self.core = core
        self.libs = {}

    def get_lib(self, lib_id, use_remote=True):
        """
        Return the corresponding lib stored if self.libs or load it if it wasn't already
        if use_remote=True, the library fetch update from Pollux or install the lib locally if it wasn't already
        """
        if not lib_id in self.libs.keys():
            path = self.id_to_path(lib_id)
            print(path)
            if os.path.exists(path):
                try:
                    if use_remote:
                        self.update(lib_id)
                    self.libs[lib_id] = importlib.import_module("castor.lib." + lib_id)
                except ModuleNotFoundError as e:
                    message = "Aucune librairie nommée '{}' n'a pu être trouvée en local".format(lib_id)
                    self.core.log(message)
                    raise Exception(message)
                except BaseException as e:
                    message = "Une erreur est survenu lors du chargement de la librairie '{}' : {}".format(lib_id, e)
                    self.core.log(message)
                    raise Exception(message)

            elif use_remote:
                # Search the lib on Pollux
                libs = self.remote_search(lib_id)
                if len(libs) == 0:
                    message = "Aucune librairie nommée '{}' n'a pu être trouvée sur Pollux".format(lib_id)
                    self.core.log(message)
                    raise Exception(message)
                self.install(lib_id)
                return self.get_lib(lib_id, use_remote)

            else:
                message = "Aucune librairie nommée '{}' n'a pu être trouvée en local".format(lib_id)
                self.core.log(message)
                raise Exception(message)

        return self.libs[lib_id]

    def require(self, id, use_remote=True):
        """
        Return an instance of the corresponding Component
        """
        return self.get_lib(id, use_remote)

    def hash(self, lib_id):
        """
        Return the hash of the file corresponding to the given lib
        """
        sha1sum = hashlib.sha1()
        with open(self.id_to_path(lib_id), 'rb') as source:
            block = source.read(2 ** 16)
            while len(block) != 0:
                sha1sum.update(block)
                block = source.read(2 ** 16)
        return sha1sum.hexdigest()

    def id_to_path(self, lib_id):
        """
        Concert the given lib_id to the correspond path to the file
        :param lib_id:
        :return:
        """
        libraryPath = os.path.dirname(__file__)
        parts = lib_id.split('.')
        fileName = "{}.py".format(parts.pop())
        libPath = os.path.join(libraryPath, *parts, fileName)
        return libPath

    def remote_search(self, lib_id):
        """
        Perform a search on Pollux for the given lib_id
        :param lib_id:
        :return:
        """
        try:
            rep = self.core.pollux.api.get("/api/lib/search", {"lib_id": lib_id})
            if rep.get("success", False):
                return rep.get("payload", {})
        except Exception as e:
            self.core.log(e)
            raise Exception(e)

    def install(self, lib_id):
        """
        Fetch the content of the corresponding lib and store it as a Python file inside
        :param lib_id:
        :return:
        """
        try:
            rep = self.core.pollux.api.get("/api/lib/i/{}/download".format(lib_id))
            if rep.get("success", False):
                payload = rep.get("payload", {})
                path = self.id_to_path(lib_id)
                # Create parent directories
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with codecs.open(path, 'w', 'utf-8') as f:
                    f.write(payload.get('content', ""))
        except Exception as e:
            message = "Impossible d'installer le lib '{}' : {}".format(lib_id, e)
            self.core.log(message)
            raise Exception(message)

    def update(self, lib_id):
        """

        :param lib_id:
        :return:
        """
        rep = self.core.pollux.api.get("/api/lib/i/{}/hash".format(lib_id))
        if rep.get("success", False):
            payload = rep.get("payload", {})
            remote_hash = payload.get("hash", None)
            if remote_hash != self.hash(lib_id):
                self.install(lib_id)
        else:
            message = "Impossible de mettre à jour la libraries '{}'".format(lib_id)
            self.core.log(message)
