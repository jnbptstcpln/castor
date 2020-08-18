
from threading import Thread
from castor import CastorCore
from .helper import get_mac_address, Logger
from .flow_wrapper import FlowWrapper
from .exception import ExitException
import time
import json


class Daemon(Thread):

    def __init__(self, name, domain="default"):
        super().__init__(daemon=True)

        self.name = name
        self.domain = domain
        self.running = False
        self.instance_id = None


        self.core = CastorCore()
        self.config = self.core.config
        self.pollux = self.core.pollux
        self.last_pollux_update = None

        self.flows = {}

        self.logger = Logger("DAEMON")

    def start(self):
        # Initiate the link with Pollux and store instance_id
        self.pollux_start()
        # Log the start
        self.log("Start daemon inside domain \"{}\" as instance {}".format(self.domain, self.instance_id))
        # Set the running flag to true
        self.running = True
        super().start()

    def _stop(self, message=None):
        # Construct the list of running wrapper
        instances = []
        for flowInstance, wrapper in self.flows.items():
            instances.append(wrapper)

        for wrapper in instances:
            try:
                wrapper.error("Arrêt du daemon {} hébergeant le processus".format(self.instance_id))
            except:
                pass

        # Log the stop
        if message:
            self.log("Stop daemon : {}".format(message))
        else:
            self.log("Stop daemon")
        self.running = False

    def stop(self):
        self._stop()


        try:
            # In order to be able to send the request we keep the daemon running
            self.running = True
            rep = self.core.pollux.api.post(
                "/api/daemons/i/{}/stop".format(self.instance_id),
                {
                    'status': json.dumps(self.status())
                }
            )
            # After sending the request we can finally stop the daemon
            self.running = False
        except BaseException:
            self.running = False
            pass



    def reload(self):
        self.core.component_library.reload()
        self.core.lib_library.reload()

    def pollux_start(self):
        try:
            rep = self.core.pollux.api.post(
                "/api/daemons/start",
                {
                    'name': self.name,
                    'domain': self.domain,
                    'machine': get_mac_address(),
                    'machine_name': self.config.daemon("machine_name", "Machine générique"),
                    'settings': json.dumps(
                        {
                            'concurrent_execution_limit': self.config.daemon("concurrent_execution_limit", 1)
                        }
                    ),
                }
            )
            if rep.get("success", False):
                payload = rep.get("payload", {})
                self.instance_id = payload.get('instance_id', None)
                self.last_pollux_update = time.time()

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
        rep = self.core.pollux.api.post(
            "/api/daemons/i/{}/fetch".format(self.instance_id),
            {
                'status': json.dumps(self.status())
            }
        )
        if rep.get("success", False):
            self.last_pollux_update = time.time()
            payload = rep.get('payload', {})
            state = payload.get('state', 'state_dead')
            queue = payload.get('queue', [])
            flows = payload.get('flows', [])

            # If Pollux tell that the daemon is dead, "force" stopping the daemon
            if state == 'state_dead':
                self._stop("Pollux considère que le daemon est mort")
                return

            try:
                for cmd in queue:
                    self.execute_command(cmd['command'], cmd['settings'])
            except ExitException:
                return

            if self.config.daemon("auto_reload", "true") == "true":
                self.reload()

            for flow in flows:
                flowInstance = flow.get("instance", None)
                flowData = flow.get("scheme", None)
                environment = flow.get("environment", None)
                try:
                    self.execute_flow(flowInstance, flowData, environment)
                except:
                    pass

        else:
            self.log("Une erreur a eu lieu lors de la requête 'fetch' vers Pollux : '{}'".format(
                rep.get("message", "Aucun message reçu depuis pollux"))
            )
            if time.time() - self.last_pollux_update > 30:
                self.log("Aucune réponse positive de Pollux depuis plus de 30 secondes, arrêt du daemon.")
                self.stop()

    def execute_flow(self, flowInstance, flowData, environment):
        try:
            if not flowInstance:
                raise Exception("Aucun identifiant d'instance spécifié")

            self.flows[flowInstance] = FlowWrapper(self, flowInstance, flowData, environment)
            self.log("Lancement du processus {} ({})".format(flowInstance, self.flows[flowInstance].flow.settings.get('name')))
            self.flows[flowInstance].start()
        except BaseException as e:
            self.log("Impossible de lancer le processus {} : {}".format(flowInstance, e))
            if flowInstance:
                self.core.pollux.api.post(
                    "/api/instances/{}/error".format(flowInstance),
                    {
                        'message': "Erreur lors de l'initialisation : \"{}\"".format(e)
                    }
                )

    def execute_command(self, command, settings):
        if command == "stop":
            self.stop()
            raise ExitException()
        elif command == "reload":
            self.reload()
        else:
            self.log("Commande inconnue : \"{}\"".format(command))

    def status(self):
        return {
            'flow_instances': len(self.flows.keys()),
            'logs': self.logger.pop()
        }

    def run(self):
        while self.running:
            self.pollux_fetch()
            # Add a tempo to the execution
            time.sleep(self.config.daemon("tempo", 1))

    def log(self, data):
        self.logger.log(data)
