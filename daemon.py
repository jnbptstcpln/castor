"""
    Example d'utilisation du daemon
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from castor import Daemon

daemon = Daemon("Daemon-Test")
daemon.start()
while daemon.running:
    pass
