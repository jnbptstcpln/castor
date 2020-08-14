
import json
from threading import Thread
import time


class FlowWrapper(Thread):

    def __init__(self, daemon, flowInstance, flow, environment):
        super().__init__()

        self.daemon = daemon
        self.flowInstance = flowInstance
        self.flow = flow
        self.last_pollux_update = time.time()
        self.environment = environment
        self.running = False

    def start(self):
        self.flow.start(self.environment)
        self.running = True
        super().start()

    def error(self, message):
        self.pollux_error(message)
        self.stop()

    def stop(self):
        if self.running:
            if self.flow.error_message is not None:
                self.daemon.log("Arrêt du processus {} suite à une erreur : {}".format(self.flowInstance, self.flow.error_message))
            else:
                self.daemon.log(
                    "Fin d'exécution du processus {}".format(self.flowInstance))

            self.flow.stop()
            self.running = False
            del self.daemon.flows[self.flowInstance]

    def pollux_update(self):

        rep = self.daemon.core.pollux.api.post(
            "/api/instances/{}/update".format(self.flowInstance),
            {
                'status': json.dumps(self.status())
            }
        )

        if rep.get("success", False):
            self.last_pollux_update = time.time()
            payload = rep.get('payload', {})

            # Stop the flow execution if it was stop on Pollux
            flowState = payload.get('state', '')
            if flowState == "state_completed":
                self.stop()

        else:
            self.log("Une erreur a eu lieu lors de la requête 'update' vers Pollux : '{}'".format(
                rep.get("message", "Aucun message reçu depuis pollux"))
            )
            if time.time() - self.last_pollux_update > 30:
                self.log("Aucune réponse positive de Pollux depuis plus de 30 secondes, arrêt du daemon.")
                self.stop()

    def pollux_complete(self):
        self.daemon.core.pollux.api.post(
            "/api/instances/{}/complete".format(self.flowInstance),
            {
                'status': json.dumps(self.status())
            }
        )

    def pollux_error(self, message):
        self.daemon.core.pollux.api.post(
            "/api/instances/{}/error".format(self.flowInstance),
            {
                'status': json.dumps(self.status()),
                'message': message
            }
        )

    def status(self):
        return {
            'environment': json.dumps(self.flow.environment.items),
            'logs': self.flow.logger.pop()
        }

    def run(self):
        while self.running:

            if not self.flow.running:
                self.stop()
                if self.flow.error_message is not None:
                    self.pollux_error(self.flow.error_message)
                else:
                    self.pollux_complete()
                return

            # If all nodes are stopped, we stop the flow
            if self.flow.number_of_running_nodes() == 0:
                self.flow.stop()

            # Update Pollux each 5 seconds
            if time.time() - self.last_pollux_update > 5:
                self.pollux_update()
