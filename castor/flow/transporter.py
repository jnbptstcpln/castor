

from castor.helper import Setting
from threading import Thread
from time import sleep


class Transporter(Thread):

    def __init__(self, links:dict, settings=None):
        super().__init__()
        self.links = links
        self.running = False
        self.settings = TransporterSettings(settings)
        self.inputs_connected = {}

    def start(self):
        self.running = True
        super().start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            for link in self.links.values():
                # Check the source is full
                if link.source.isset:
                    # Compute if we flush value from source to targets
                    # If any target port's buffer is full, cancel the flush
                    flush = True
                    for target_id, target in link.targets.items():
                        if target.is_buffer_full:
                            flush = False
                    if flush:
                        # Push value to target
                        for target_id, target in link.targets.items():
                            target.push(link.source.value)
                        # Clear source
                        link.source.clear()
            # To not overwhelm the cpu we set a tempo of 1s between iteration
            sleep(self.settings.tempo)

    def is_input_connected(self, port_id):
        if not port_id in self.inputs_connected.keys():
            self.inputs_connected[port_id] = self._is_input_connected(port_id)
        return self.inputs_connected[port_id]

    def _is_input_connected(self, port_id):
        for link in self.links.values():
            for target_id, target in link.targets.items():
                if target_id == port_id:
                    return True
        return False

    def node_children_id(self, node_id):
        nodes_id = []
        for source_id, link in self.links.items():
            if source_id.split(':')[0] == node_id:
                for target_id in link.targets.keys():
                    nodes_id.append(target_id.split(':')[0])
        return nodes_id



class TransporterSettings(Setting):
    @property
    def tempo(self):
        return self.get("tempo", 0.1)
