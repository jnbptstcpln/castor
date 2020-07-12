from configparser import ConfigParser

class Setting:

    def __init__(self, settings):
        if type(settings) == dict:
            self.settings = settings
        else:
            self.settings = {}

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
            matches = re.search(r"^:(\w+) ([^:]+):?([^:]+)?:?([^:]+)?", line.strip())
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


class Config(ConfigParser):

    def __init__(self, core):
        super().__init__()
        import os
        self.core = core
        # Read config file
        self.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini"))
