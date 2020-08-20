"""
    Example d'utilisation du daemon
"""
import os
import sys
import time
import copy
import json
import getopt
import threading

# Make sure `castor` is in path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from castor import CastorCore

class DaemonWrapper(threading.Thread):

    def __init__(self):
        super().__init__()
        args = self._parse_args()
        self.flowFile = args.get("flow", None)
        self.core = CastorCore()
        self.environment = args.get("environment", {})
        self.running = False

        try:
            self.flow = self.core.open(self.flowFile)
        except BaseException as e:
            print("\033[91mErreur lors de l'initialisation du processus : {}\033[0m".format(e))
            exit(3)

    def start(self):
        try:
            self.flow.start(self.environment)
            self.running = True
        except BaseException as e:
            print(type(e))
            print("\033[91mErreur lors du démarrage du processus : {}\033[0m".format(e))
            exit(3)
        super().start()

    def stop(self):
        if self.running:
            self.flow.stop()
            self.running = False

    def run(self):
        while self.running:

            if not self.flow.running:

                if self.flow.restarting:

                    # Keep the same logger to keep logs
                    logger = self.flow.logger
                    # Deep copying the environment (initial or current)
                    environment = copy.deepcopy(self.flow.environment_initial.items)
                    if self.flow.keep_environment:
                        environment = copy.deepcopy(self.flow.environment.items)
                    # build a brand new flos
                    self.flow = self.core.open(self.flowFile)
                    # Set the logger
                    self.flow.logger = logger
                    # Start with the environment
                    self.flow.start(environment)
                else:
                    self.stop()

            # If all nodes are stopped, we stop the flow
            if self.flow.number_of_running_nodes() == 0:
                self.flow.stop()

            time.sleep(5)

    def _parse_args(self):

        args = {}

        try:
            opts, _args = getopt.getopt(sys.argv[1:], "", ["flow=", "domain="])
        except getopt.GetoptError:
            print("python3 daemon.py --flow [flow_file] --environment [environment]")
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("--flow"):
                args["flow"] = arg
            elif opt in ("--environment"):
                args["environment"] = json.loads(arg)

        return args


wrapper = DaemonWrapper()
wrapper.start()
wrapper.join()
