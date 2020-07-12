

from castor.helper import Setting
from .transporter import Transporter
from .node import Node
from .link import Link


class Flow:

    def __init__(self, nodes:dict, links:list, settings=None):
        self.nodes = nodes
        self.links = links
        self.settings = FlowSettings(settings)
        self.transporter = Transporter(self.links, self.settings.transporter)
        self.running = False

    def start(self):
        self.running = True
        for id, node in self.nodes.items():
            # Put a reference of the flow inside each node
            node.flow = self
            node.start()
        self.transporter.start()

    def stop(self):
        if self.running:
            self.running = False
            for id, node in self.nodes.items():
                node.stop()
            self.transporter.stop()


class FlowSettings(Setting):
    @property
    def transporter(self):
        return self.get('transporter', None)
