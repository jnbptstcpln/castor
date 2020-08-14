
import time
from castor.helper import Setting, Logger
from .transporter import Transporter
from .environment import Environment


class Flow:

    def __init__(self, nodes:dict, links:dict, settings=None):
        self.nodes = nodes
        self.links = links
        self.settings = FlowSettings(settings)
        self.environment = Environment()
        self.transporter = Transporter(self.links, self.settings.transporter)
        self.running = False
        self.error_message = None
        self.logger = Logger("FLOW")

    def start(self, environment:dict=None):
        try:
            self.environment.build(environment)
            self.running = True
            for id, node in self.nodes.items():
                # Put a reference of the flow inside each node
                node.flow = self
                node.start()
            self.transporter.start()
        except BaseException as e:
            self.error(e)

    def error(self, message):
        self.stop()
        self.error_message = message

    def stop(self):
        if self.running:
            self.running = False
            for id, node in self.nodes.items():
                node.stop()
            self.transporter.stop()

    def log(self, data):
        self.logger.log(data)


class FlowSettings(Setting):
    @property
    def transporter(self):
        return self.get('transporter', None)
