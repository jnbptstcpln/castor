

from castor.helper import Setting
from threading import Thread
from time import sleep


class Transporter(Thread):

    def __init__(self, links:dict, settings=None):
        super().__init__()
        self.links = links
        self.running = False
        self.settings = TransporterSettings(settings)

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
                    for target in link.targets:
                        if target.is_buffer_full:
                            flush = False
                    if flush:
                        # Push value to target
                        for target in link.targets:
                            target.push(link.source.value)
                        # Clear source
                        link.source.clear()
            # To not overwhelm the cpu we set a tempo of 1s between iteration
            sleep(self.settings.tempo)


class TransporterSettings(Setting):
    @property
    def tempo(self):
        return self.get("tempo", 0.1)
