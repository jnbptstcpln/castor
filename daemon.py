"""
    Example d'utilisation du daemon
"""
import time
from castor import Daemon



print("Press any key during execution to stop the daemon")

daemon = Daemon("Daemon-Test")
daemon.start()
input()
daemon.stop()