
import time
from configparser import ConfigParser

class Setting:

    def __init__(self, settings):
        if type(settings) == dict:
            self.settings = settings
        else:
            self.settings = {}

    def set(self, key, value):
        self.settings[key] = value

    def get(self, key, default=None):
        return self.settings.get(key, default)


class Doc:
    def __init__(self, entity):
        import re
        self.entity = entity
        self.doc = self.entity.__doc__
        self.entities = {}
        # Parse the document
        for line in self.doc.split("\n"):
            matches = re.search(r"^:(\w+) ([^:]+):?([^:]+)?:?(.*)", line.strip())
            if matches:
                name = matches.group(1)
                data = []
                for groupNum in range(1, len(matches.groups())):
                    groupNum = groupNum + 1
                    data.append(matches.group(groupNum))
                if not name in self.entities.keys():
                    self.entities[name] = []
                self.entities[name].append(data)

    @property
    def version(self):
        versions = self.entities.get("version", [])
        if len(versions) > 0:
            return versions[0][0]
        return "Unknown"

    @property
    def inputs(self):
        params = []
        _params = self.entities.get("param", [])
        for param in _params:
            params.append({
                'name': param[0],
                'type': param[1],
                'description': param[2],
            })
        return params

    @property
    def outputs(self):
        returns = []
        _returns = self.entities.get("return", [])
        for output in _returns:
            returns.append({
                'name': output[0],
                'type': output[1],
                'description': output[2],
            })
        return returns

    @property
    def settings(self):
        settings = []
        _settings = self.entities.get("setting", [])
        for output in _settings:
            settings.append({
                'name': output[0],
                'type': output[1],
                'description': output[2],
            })
        return settings

    @property
    def requirements(self):
        requirements = []
        _requirements = self.entities.get("require", [])
        for output in _requirements:
            requirements.append({
                'name': output[0]
            })
        return requirements


class Config(ConfigParser):

    def __init__(self, core, config=None):
        super().__init__()
        import os
        self.core = core
        # Read config file
        if config is None:
            self.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini"))
        else:
            if os.path.isfile(config):
                self.read(config)
            else:
                raise FileNotFoundError("Le fichier de configuration \"{}\" n'existe pas".format(config))

    def pollux(self, key, default=None):
        return self.get("pollux", key, fallback=default)

    def castor(self, key, default=None):
        return self.get("castor", key, fallback=default)

    def daemon(self, key, default=None):
        return self.get("daemon", key, fallback=default)

class Logger:

    def __init__(self, name="GENERAL"):
        self.name = name
        self.buffer = []
        self.logs = []

    def log(self, message):
        print("{}> {}".format(self.name, message))
        self.logs.append({
            'time': int(round(time.time() * 1000)),
            'message': message
        })
        self.buffer.append({
            'time': int(round(time.time() * 1000)),
            'message': message
        })

    def pop(self):
        temp = self.buffer
        self.buffer = []
        return temp

def get_mac_address():
    import uuid
    return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
