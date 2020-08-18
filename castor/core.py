
import time
from .flow import ComponentLibrary, Flow, Node, Link
from .helper import Config
from .pollux import Pollux
from .lib import Library as LibLibrary

import json


class Core:

    def __init__(self, config=None):
        self.config = Config(self, config)
        self.component_library = ComponentLibrary(self)
        self.lib_library = LibLibrary(self)
        self.pollux = Pollux(self)
        self.logs = []

    def open(self, file):
        return self.build_flow(json.load(open(file)))

    def build_flow(self, flowData:dict):
        # Create all node and save inputs and outputs reference
        nodes = {}
        inputs = {}
        outputs = {}
        for _node in flowData.get('nodes', []):
            # Create the node with id, an instance of component get from component_library (node is use as component's settings)
            # and node's settings with _node
            node = Node(_node.get('id'), self.component_library.get(_node.get('component'), _node), _node)

            # Try to fullfil node's component lib's requirements
            requirements_errors = []
            for requirement in node.component.doc.requirements:
                try:
                    self.lib_library.require(requirement['name'])
                except BaseException as e:
                    raise e

            # Store reference for each inputs
            for name, port in node.inputs.items():
                inputs['{}:{}'.format(node.id, name)] = port
            # Store reference for each outputs
            for name, port in node.outputs.items():
                outputs['{}:{}'.format(node.id, name)] = port
            # Add the node to the nodes dict
            nodes[node.id] = node

        # Create links between ports
        links = {}
        for _link in flowData.get('links', []):
            try:
                source = outputs[_link.get('source')]
            except KeyError:
                raise Exception(
                    "Erreur lors de la création du lien : aucun port ne correspond à '{}'".format(_link.get('source')))
            targets = {}
            for target_id in _link.get('targets', []):
                try:
                    targets[target_id] = inputs[target_id]
                except KeyError:
                    raise Exception(
                        "Erreur lors de la création du lien : aucun port ne correspond à '{}'".format(target_id))
            links[_link.get('source')] = Link(source, targets)

        return Flow(nodes, links, flowData.get("settings"))

    def log(self, data):
        self.logs.append({
            'time': time.time(),
            'data': data
        })
