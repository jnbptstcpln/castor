
from threading import Thread
from castor import CastorCore
import time


class Daemon(Thread):

    def __init__(self):
        super().__init__(daemon=True)

        self.running = False
        self.instance_id = None

        self.core = CastorCore()
        self.config = self.core.config
        self.pollux = self.core.pollux
        self.logs = []

    def start(self):
        # Initiate the link with Pollux and store instance_id
        self.pollux_start()
        # Log the start
        self.log("Start daemon with instance_id={}".format(self.instance_id))
        # Set the running flag to true
        self.running = True
        super().start()

    def stop(self):
        # Log the stop
        self.log("Stop daemon".format(self.instance_id))
        self.running = False

    def pollux_start(self):
        try:
            rep = self.core.pollux.api.post("/api/daemons/start", {'name': self.config.daemon("name", "NO_NAME")})
            if rep.get("success", False):
                payload = rep.get("payload", {})
                self.instance_id = payload.get('instance_id', None)

            # If no instance_id was gotten from Pollux, log and raise an exception
            if self.instance_id is None:
                raise Exception(
                    "Impossible de lancer le deamon, une erreur a lieu lors de la connexion à Pollux : '{}'"
                        .format(
                            rep.get("message", "Aucun message reçu depuis pollux")
                        )
                )
        except Exception as e:
            self.log(e)
            raise Exception(e)

    def pollux_fetch(self):
        rep = self.core.pollux.api.get("/api/daemons/i/{}/fetch".format(self.instance_id))
        if rep.get("success", False):
            payload = rep.get('payload', {})
            # TODO: Execute received commands
        else:
            self.log("Une erreur a eu lieu lors de la requête 'fetch' vers Pollux : '{}'".format(
                rep.get("message", "Aucun message reçu depuis pollux"))
            )

    def run(self):
        while True:
            self.pollux_fetch()
            # Add a tempo to the execution
            time.sleep(self.config.daemon("tempo", 5))

    def log(self, data):
        self.logs.append({
            'time': time.time(),
            'data': data
        })
