
import requests


class Pollux:

    def __init__(self, core):
        self.core = core
        self.config = self.core.config
        self.api = PolluxAPI(self)


class PolluxAPI:

    def __init__(self, pollux):
        self.pollux = pollux
        self.config = self.pollux.config

    def get(self, url, params=None):
        if params is None:
            params = {}
        rep = requests.get(
            "{}{}".format(self.config.pollux('host'), url),
            headers=self.headers,
            params=params
        )
        try:
            return rep.json()
        except ValueError as e:
            raise ValueError("La réponse du serveur est incorrecte : {}".format(rep.text), e)

    def post(self, url, data=None):
        if data is None:
            data = {}
        rep = requests.post(
            "{}{}".format(self.config.pollux('host'), url),
            headers=self.headers,
            data=data
        )
        try:
            return rep.json()
        except ValueError as e:
            raise ValueError("La réponse du serveur est incorrecte : {}".format(rep.text), e)

    @property
    def headers(self):
        return {
            'X-API-KEY': self.config.pollux("key")
        }
