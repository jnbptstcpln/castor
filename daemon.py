"""
    Example d'utilisation du daemon
"""
import os
import sys
import time
import getopt
import threading

# Make sure `castor` is in path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from castor import Daemon
from requests.exceptions import ConnectionError


class DaemonWrapper(threading.Thread):

    def __init__(self):
        super().__init__()
        args = self._parse_args()
        try:
            self._daemon = Daemon(
                name=args.get("name", "Daemon-Generic"),
                domain=args.get("domain", "default"),
                config=args.get("config", None)
            )
        except BaseException as e:
            print("\033[91mErreur lors de la création du daemon : {}\033[0m".format(e))
            exit(3)

    def start(self):
        try:
            self._daemon.start()
        except ConnectionError as e:
            print("\033[91mErreur lors du démarrage du daemon : impossible de se connecter à {}\033[0m".format(self._daemon.pollux.config.pollux('host')))
        except BaseException as e:
            print(type(e))
            print("\033[91mErreur lors du démarrage du daemon : {}\033[0m".format(e))
            exit(3)
        super().start()

    def run(self):
        while self._daemon.running:
            time.sleep(5)

    def _parse_args(self):

        args = {}

        try:
            opts, _args = getopt.getopt(sys.argv[1:], "", ["name=", "domain=", "config="])
        except getopt.GetoptError:
            print("python3 daemon.py --name [daemon_name] --domain [daemon_domain] --config [config_file]")
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("--name"):
                args["name"] = arg
            elif opt in ("--domain"):
                args["domain"] = arg
            elif opt in ("--config"):
                args["config"] = arg

        return args


wrapper = DaemonWrapper()
wrapper.start()
wrapper.join()
